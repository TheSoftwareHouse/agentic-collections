#!/usr/bin/env node
/**
 * PreToolUse guard for Jira write operations in tsh-product-management.
 *
 * Enforces two policies that prose alone cannot:
 *
 *   1. Gate 2 — no Jira create/update/transition before the user has approved
 *      the formatted backlog. Approval is recorded in
 *      `specifications/<workshop>/.gates.md` by the
 *      `orchestrating-business-analysis` skill, and it is SCOPED: the Gate 2 row
 *      names the target project key, and a write is allowed only when every
 *      project it targets is named by an approved row in a live ledger.
 *
 *   2. Protected Status Policy — a task whose block in `jira-tasks.md` carries a
 *      🔒 in its heading, or a Status of Done, Cancelled, or PO APPROVE, is
 *      immutable and must never be updated.
 *
 * Archived artifacts do not exist for this guard: any path under a `sessions`
 * directory is skipped. Otherwise workshop one's approved ledger would hold the
 * gate open for workshop two forever, and a stale archived 🔒 would block a
 * legitimately reopened issue with no recovery path.
 *
 * One residual this guard cannot close: two live (unarchived) workshops pushing
 * to the SAME project share gate state, because a tool call carries no signal of
 * which workshop it serves. Project scoping narrows the blast radius to that one
 * project; prompt archiving after verification (which the workflow already
 * mandates) removes it.
 *
 * Contract: reads the PreToolUse payload as JSON on stdin. Emits a deny decision
 * as JSON on stdout when a policy is violated; stays silent (exit 0) when the
 * call is allowed, so normal permission rules still apply on top.
 *
 * Failure mode is deliberate: an unreadable or missing gate ledger means "not
 * approved", so it denies. An internal error in the hook itself falls back to
 * "ask" rather than silently allowing or blocking.
 */

import { readFileSync, readdirSync, existsSync, statSync } from "node:fs";
import { join } from "node:path";

/**
 * Tool-name matching is deliberately prefix-agnostic. The Atlassian MCP server
 * may be wired up as a plain `atlassian` server (`mcp__atlassian__*`) or as a
 * managed connector with a different key (`mcp__atlassian-rovo__*`, etc.), so
 * matching on a hardcoded `mcp__atlassian__` prefix would silently never fire.
 */
const ATLASSIAN_TOOL_PATTERN = /^mcp__.*(atlassian|jira|rovo|confluence)/i;

/**
 * Classification is an explicit read allowlist with a gated default, and every
 * pattern is ANCHORED to the start of the bare tool name.
 *
 * Unanchored substring matching was wrong in both directions. It denied reads:
 * `getTransitionsForJiraIssue`, `getIssueLinkTypes` and the Confluence comment
 * readers all contain a write noun (`transition`, `link`, `comment`), so they
 * failed the read test and hit the gate — and the first of those is required by
 * the workflow's own "check the status before updating" rule, which made the
 * gate block the read that exists to protect the write. And it allowed writes:
 * a bare `me` matched `merge` and `rename`, so `mergeJiraIssues` would have
 * classified as a read and skipped the gate entirely.
 *
 * Anything unrecognized is treated as a potential write rather than waved
 * through, so a future server version cannot re-open the hole by adding a verb
 * nobody listed here.
 */
const READ_PREFIXES =
  /^(get|search|list|read|fetch|lookup|view|find|query|describe|count|export|download)/i;
const WRITE_PREFIXES =
  /^(create|edit|update|transition|delete|remove|add|move|rank|assign|comment|link|unlink|set|merge|rename|archive|restore|publish|upload|attach|clone|convert|import|post|put|patch)/i;

/**
 * Reads whose names do not start with a verb. `atlassianUserInfo` is the reason
 * `info` used to be in the read pattern; an exact entry buys the same allowance
 * without letting `info` match anywhere inside a name.
 */
const READ_EXACT = new Set(["atlassianuserinfo", "userinfo", "whoami", "me"]);

/** @returns {"read"|"write"|"unknown"} */
function classify(bareName) {
  if (READ_EXACT.has(bareName.toLowerCase())) return "read";
  if (READ_PREFIXES.test(bareName)) return "read";
  if (WRITE_PREFIXES.test(bareName)) return "write";
  return "unknown";
}

/**
 * The bare tool name is everything after the LAST `__`.
 *
 * A plugin-provided server is named `mcp__plugin_<plugin>_<server>__<tool>`, and
 * that is the default case here because tsh-core bundles Atlassian. Stripping
 * only `^mcp__[^_]*(__)?` left `_tsh-core_atlassian__editJiraIssue` as the "bare"
 * name — harmless today only because no server key happens to contain a listed
 * verb, and silently wrong the moment one does.
 */
function bareToolName(toolName) {
  const lastSeparator = toolName.lastIndexOf("__");
  return lastSeparator === -1 ? toolName : toolName.slice(lastSeparator + 2);
}

const KEY_FIELD_PATTERN = /(^|_)(issueIdOrKey|issueKey|issueid|key|issues|issueKeys)($|_)/i;
const PROJECT_FIELD_PATTERN = /(^|_)(projectKey|projectKeyOrId|projectIdOrKey|project)($|_)/i;
const ISSUE_KEY_PATTERN = /\b([A-Z][A-Z0-9_]{1,19}-\d+)\b/g;
const PROJECT_KEY_VALUE_PATTERN = /^[A-Z][A-Z0-9_]{1,19}$/;
const MAX_SCAN_DEPTH = 6;

/**
 * Artifacts that mark a session as BA work. Without one of these the gate
 * concept does not apply, so the guard stands down — otherwise a user-level
 * install of this hook would block ordinary Jira use in unrelated projects.
 */
const BA_ARTIFACTS = [".gates.md", "jira-tasks.md", "extracted-tasks.md"];

/**
 * `pushing-to-jira.md` step 11 archives a workshop's artifacts under
 * `specifications/projects/<p>/sessions/<date>-<workshop>/`. Everything below a
 * directory with this name is history, not live gate state.
 */
const ARCHIVE_DIR = "sessions";

function decide(decision, reason) {
  process.stdout.write(
    JSON.stringify({
      hookSpecificOutput: {
        hookEventName: "PreToolUse",
        permissionDecision: decision,
        permissionDecisionReason: reason,
      },
    })
  );
  process.exit(0);
}

function allow() {
  // Emit nothing: the call falls through to the normal permission flow.
  process.exit(0);
}

function readStdin() {
  try {
    return readFileSync(0, "utf8");
  } catch {
    return "";
  }
}

/**
 * ONE traversal collects every file this guard reads, keyed by filename.
 *
 * The matcher fires on every Atlassian call, so each recursive walk here is a
 * per-call cost paid in a fresh node process. The previous shape ran five
 * independent walks over the same tree (three for the BA-artifact probe, one
 * for jira-tasks.md, one for the ledgers); this runs exactly one.
 *
 * Skips noisy directories and the `sessions` archive tree — archived ledgers
 * and task files are not live state.
 */
function scanForArtifacts(dir, targets, depth = 0, found = null) {
  if (found === null) {
    found = new Map();
    for (const name of targets) found.set(name, []);
  }
  if (depth > MAX_SCAN_DEPTH) return found;
  let entries;
  try {
    entries = readdirSync(dir, { withFileTypes: true });
  } catch {
    return found;
  }
  for (const entry of entries) {
    const full = join(dir, entry.name);
    if (entry.isDirectory()) {
      if (
        entry.name === "node_modules" ||
        entry.name === ".git" ||
        entry.name === "dist" ||
        entry.name === "build" ||
        entry.name === ARCHIVE_DIR ||
        // `.claude` is the one dotdirectory a team plausibly keeps project
        // files in, so it stays scanned while other dotdirectories are noise.
        (entry.name.startsWith(".") && entry.name !== ".claude")
      ) {
        continue;
      }
      scanForArtifacts(full, targets, depth + 1, found);
    } else if (found.has(entry.name)) {
      found.get(entry.name).push(full);
    }
  }
  return found;
}

function readText(path) {
  try {
    return readFileSync(path, "utf8");
  } catch {
    return "";
  }
}

/**
 * Approved Gate 2 rows of a ledger, verbatim. Row shape:
 *   | 2 | jira-tasks.md | approved | 2026-08-19 14:32 — project ACME, batch push |
 * The trailing cell must name the target project key — approval is per project,
 * and `approvedForProject` below matches against the row text.
 */
function approvedGate2Rows(ledgerText) {
  return ledgerText
    .split("\n")
    .filter((line) => /^\s*\|\s*2(\.0)?\s*\|/.test(line))
    .filter((line) => /\bapproved\b/i.test(line) && !/\bnot\s+approved\b/i.test(line));
}

/**
 * Case-sensitive word match: Jira project keys are uppercase by convention
 * (`PROJECT_KEY_VALUE_PATTERN` enforces it), so `ACME` cannot collide with prose
 * like "batch push". Keys are [A-Z0-9_]+ — no regex metacharacters to escape.
 */
function approvedForProject(approvedRows, projectKey) {
  const asWord = new RegExp(`\\b${projectKey}\\b`);
  return approvedRows.some((row) => asWord.test(row));
}

/** Collect issue keys from fields that plausibly identify a target issue. */
function targetIssueKeys(toolInput) {
  const keys = new Set();
  const visit = (node, fieldName, depth) => {
    if (depth > 5 || node == null) return;
    if (typeof node === "string") {
      if (fieldName && KEY_FIELD_PATTERN.test(fieldName)) {
        for (const match of node.matchAll(ISSUE_KEY_PATTERN)) keys.add(match[1]);
      }
      return;
    }
    if (Array.isArray(node)) {
      for (const item of node) visit(item, fieldName, depth + 1);
      return;
    }
    if (typeof node === "object") {
      for (const [childName, value] of Object.entries(node)) {
        visit(value, childName, depth + 1);
      }
    }
  };
  visit(toolInput, null, 0);
  return [...keys];
}

/**
 * The project keys a call targets: prefixes of any issue keys in the payload,
 * plus bare project-key fields (creates carry `projectKey`, not an issue key).
 */
function targetProjectKeys(toolInput) {
  const projects = new Set();
  for (const issueKey of targetIssueKeys(toolInput)) {
    projects.add(issueKey.slice(0, issueKey.lastIndexOf("-")));
  }
  const visit = (node, fieldName, depth) => {
    if (depth > 5 || node == null) return;
    if (typeof node === "string") {
      if (
        fieldName &&
        PROJECT_FIELD_PATTERN.test(fieldName) &&
        PROJECT_KEY_VALUE_PATTERN.test(node.trim())
      ) {
        projects.add(node.trim());
      }
      return;
    }
    if (Array.isArray(node)) {
      for (const item of node) visit(item, fieldName, depth + 1);
      return;
    }
    if (typeof node === "object") {
      for (const [childName, value] of Object.entries(node)) {
        visit(value, childName, depth + 1);
      }
    }
  };
  visit(toolInput, null, 0);
  return [...projects];
}

const BLOCK_HEADING_PATTERN = /^#{2,4}\s/;
const PROTECTED_MARK = "\u{1F512}"; // 🔒
const JIRA_KEY_LINE_PATTERN = /^\s*\*{0,2}jira\s*key\*{0,2}\s*:/i;
const STATUS_LINE_PATTERN = /^\s*\*{0,2}status\*{0,2}\s*:/i;
const PROTECTED_STATUS_PATTERN = /\b(done|cancelled|canceled|po\s+approve)\b/i;

/**
 * Which of `candidateKeys` are protected in the live `jira-tasks.md` files.
 *
 * The benchmark template puts `**Jira Key**:` and `**Status**:` on their own
 * lines under a `###` task heading, and the 🔒 marker in the heading itself —
 * so a task is parsed as a BLOCK, never as one line. A block is protected when
 * its heading carries 🔒 (or the word PROTECTED), or its Status line names a
 * protected status. Keys are read from the Jira Key line only: a block whose
 * prose merely mentions "blocked by ACME-441" must not protect ACME-441.
 *
 * A single line carrying both a candidate key and the 🔒 marker also counts, so
 * inline notations ("ACME-441 — status: Done 🔒") stay recognized.
 */
function protectedKeys(jiraTaskFiles, candidateKeys) {
  if (candidateKeys.length === 0) return [];
  const wanted = new Set(candidateKeys);
  const hits = new Set();
  for (const path of jiraTaskFiles) {
    const lines = readText(path).split("\n");
    let blockKeys = [];
    let blockProtected = false;
    const closeBlock = () => {
      if (blockProtected) {
        for (const key of blockKeys) if (wanted.has(key)) hits.add(key);
      }
      blockKeys = [];
      blockProtected = false;
    };
    for (const line of lines) {
      if (BLOCK_HEADING_PATTERN.test(line)) {
        closeBlock();
        if (line.includes(PROTECTED_MARK) || /\bPROTECTED\b/.test(line)) {
          blockProtected = true;
        }
        continue;
      }
      if (JIRA_KEY_LINE_PATTERN.test(line)) {
        for (const match of line.matchAll(ISSUE_KEY_PATTERN)) blockKeys.push(match[1]);
      } else if (STATUS_LINE_PATTERN.test(line) && PROTECTED_STATUS_PATTERN.test(line)) {
        blockProtected = true;
      }
      if (line.includes(PROTECTED_MARK)) {
        for (const match of line.matchAll(ISSUE_KEY_PATTERN)) {
          if (wanted.has(match[1])) hits.add(match[1]);
        }
      }
    }
    closeBlock();
  }
  return [...hits];
}

function main() {
  const raw = readStdin();
  if (!raw.trim()) allow();

  let payload;
  try {
    payload = JSON.parse(raw);
  } catch {
    decide("ask", "BA guard could not parse the PreToolUse payload. Confirm this Jira write manually.");
  }

  const toolName = payload.tool_name || payload.toolName || "";

  // 1. Not an Atlassian/Jira tool at all.
  if (!ATLASSIAN_TOOL_PATTERN.test(toolName)) allow();

  // 2. Read-only Atlassian call. Checked before any filesystem work so that
  //    fetching issues and searching boards stays fast and never prompts.
  const kind = classify(bareToolName(toolName));
  if (kind === "read") allow();

  const cwd = payload.cwd || process.cwd();
  if (!existsSync(cwd) || !statSync(cwd).isDirectory()) {
    decide("ask", "BA guard could not resolve the working directory. Confirm this Jira write manually.");
  }

  // 3. Is this a BA session? Without live BA artifacts on disk there is no gate
  //    to enforce, so stand down and let normal permission rules apply. This
  //    keeps a user-level install from blocking ordinary Jira work in other
  //    projects — and archived-only repositories count as no BA session.
  //    The same single scan also feeds the protected-task and ledger checks.
  const artifacts = scanForArtifacts(cwd, BA_ARTIFACTS);
  if (BA_ARTIFACTS.every((name) => artifacts.get(name).length === 0)) allow();

  const toolInput = payload.tool_input || payload.toolInput || {};

  // A recognized write that fails a policy is denied. An unrecognized tool is
  // held for the user with `ask` instead: the guard is reporting that it could
  // not classify the call, which is a question, not a policy violation. Either
  // way the model cannot proceed on its own.
  const verdict = kind === "write" ? "deny" : "ask";
  const unclassified =
    kind === "write"
      ? ""
      : `BA guard could not classify "${bareToolName(toolName)}" as a read or a write, ` +
        "so it is being treated as a potential write. ";

  // Policy 2 first: a protected issue is never writable, gate or no gate.
  // Only live jira-tasks.md files count — an archived copy marking a key 🔒
  // must not block an issue whose status was legitimately reopened since.
  const blocked = protectedKeys(artifacts.get("jira-tasks.md"), targetIssueKeys(toolInput));
  if (blocked.length > 0) {
    decide(
      verdict,
      unclassified +
        `Protected Status Policy: ${blocked.join(", ")} ${
          blocked.length === 1 ? "is" : "are"
        } recorded in jira-tasks.md with a protected status (Done, Cancelled, or PO APPROVE) or a 🔒 marker, ` +
        "and cannot be modified. Tell the user the status must be changed in Jira and the backlog " +
        "re-imported first — re-importing refreshes jira-tasks.md and clears a stale marker."
    );
  }

  // Policy 1: Gate 2 must be approved in a LIVE ledger, for the project this
  // write targets. An approval names its project; it unlocks nothing else.
  const ledgers = artifacts.get(".gates.md");
  if (ledgers.length === 0) {
    decide(
      verdict,
      unclassified +
        "Gate 2 not approved: no live gate ledger found (expected specifications/<workshop>/.gates.md; " +
        "archived ledgers under sessions/ do not count). " +
        "Create the ledger, complete Gates 0/1/1.5, and record explicit Gate 2 approval before pushing to Jira."
    );
  }

  const approvedRows = ledgers.flatMap((path) => approvedGate2Rows(readText(path)));
  if (approvedRows.length === 0) {
    decide(
      verdict,
      unclassified +
        `Gate 2 not approved: found ${ledgers.length} live gate ledger(s) but none records Gate 2 as approved. ` +
        "Present the formatted tasks, get explicit user approval for the target Jira project, " +
        "record it in the ledger's Gate 2 row (naming the project key), then retry."
    );
  }

  const projects = targetProjectKeys(toolInput);
  const uncovered = projects.filter((key) => !approvedForProject(approvedRows, key));
  if (uncovered.length > 0) {
    decide(
      verdict,
      unclassified +
        `Gate 2 approval does not cover project ${uncovered.join(", ")}: an approved Gate 2 row exists, ` +
        "but its scope names a different project. Approval is per project — get explicit user approval " +
        `for ${uncovered.join(", ")} and record it in the Gate 2 row (e.g. "project ${uncovered[0]}") before retrying.`
    );
  }

  // A write whose payload names no project at all (rare) falls back to the
  // ledger-level check above: some live ledger has an approved Gate 2 row.
  allow();
}

try {
  main();
} catch (error) {
  decide("ask", `BA guard failed unexpectedly (${error && error.message}). Confirm this Jira write manually.`);
}
