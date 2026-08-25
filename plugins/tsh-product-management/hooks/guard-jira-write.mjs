#!/usr/bin/env node
/**
 * PreToolUse guard for Jira write operations in tsh-product-management.
 *
 * Enforces two policies that prose alone cannot:
 *
 *   1. Gate 2 — no Jira create/update/transition before the user has approved
 *      the formatted backlog. Approval is recorded in
 *      `specifications/<workshop>/.gates.md` by the
 *      `orchestrating-business-analysis` skill.
 *
 *   2. Protected Status Policy — issues marked `🔒` in `jira-tasks.md` (status
 *      Done, Cancelled, or PO APPROVE) are immutable and must never be updated.
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
const READ_VERB_PATTERN = /(get|search|list|read|fetch|lookup|view|find|query|info|me)/i;
const WRITE_VERB_PATTERN = /(create|edit|update|transition|delete|remove|add|move|rank|assign|comment|link|set)/i;

const KEY_FIELD_PATTERN = /(^|_)(issueIdOrKey|issueKey|issueid|key|issues|issueKeys)($|_)/i;
const ISSUE_KEY_PATTERN = /\b([A-Z][A-Z0-9_]{1,19}-\d+)\b/g;
const MAX_SCAN_DEPTH = 6;

/**
 * Artifacts that mark a session as BA work. Without one of these the gate
 * concept does not apply, so the guard stands down — otherwise a user-level
 * install of this hook would block ordinary Jira use in unrelated projects.
 */
const BA_ARTIFACTS = [".gates.md", "jira-tasks.md", "extracted-tasks.md"];

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

/** Find files named `target` under `dir`, skipping noisy directories. */
function findFiles(dir, target, depth = 0, found = []) {
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
        (entry.name.startsWith(".") && entry.name !== ".claude")
      ) {
        continue;
      }
      findFiles(full, target, depth + 1, found);
    } else if (entry.name === target) {
      found.push(full);
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
 * A ledger approves Gate 2 when its Gate 2 row is marked approved.
 * Row shape: | 2 | jira-tasks.md | approved | 2026-08-19 14:32 — project ACME |
 */
function gate2Approved(ledgerText) {
  return ledgerText
    .split("\n")
    .filter((line) => /^\s*\|\s*2(\.0)?\s*\|/.test(line))
    .some((line) => /\bapproved\b/i.test(line) && !/\bnot\s+approved\b/i.test(line));
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

/** An issue is protected when its line in jira-tasks.md carries the 🔒 marker. */
function protectedKeys(cwd, candidateKeys) {
  if (candidateKeys.length === 0) return [];
  const hits = [];
  for (const path of findFiles(cwd, "jira-tasks.md")) {
    const lines = readText(path).split("\n");
    for (const key of candidateKeys) {
      const marked = lines.some(
        (line) => line.includes(key) && (line.includes("\u{1F512}") || /\bPROTECTED\b/i.test(line))
      );
      if (marked && !hits.includes(key)) hits.push(key);
    }
  }
  return hits;
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
  const bareName = toolName.replace(/^mcp__[^_]*(__)?/, "");
  if (READ_VERB_PATTERN.test(bareName) && !WRITE_VERB_PATTERN.test(bareName)) allow();

  const cwd = payload.cwd || process.cwd();
  if (!existsSync(cwd) || !statSync(cwd).isDirectory()) {
    decide("ask", "BA guard could not resolve the working directory. Confirm this Jira write manually.");
  }

  // 3. Is this a BA session? Without BA artifacts on disk there is no gate to
  //    enforce, so stand down and let normal permission rules apply. This keeps
  //    a user-level install from blocking ordinary Jira work in other projects.
  const baArtifacts = BA_ARTIFACTS.flatMap((name) => findFiles(cwd, name));
  if (baArtifacts.length === 0) allow();

  const toolInput = payload.tool_input || payload.toolInput || {};

  // Policy 2 first: a protected issue is never writable, gate or no gate.
  const blocked = protectedKeys(cwd, targetIssueKeys(toolInput));
  if (blocked.length > 0) {
    decide(
      "deny",
      `Protected Status Policy: ${blocked.join(", ")} ${
        blocked.length === 1 ? "is" : "are"
      } marked 🔒 in jira-tasks.md (status Done, Cancelled, or PO APPROVE) and cannot be modified. ` +
        "Tell the user the status must be changed in Jira and the backlog re-imported first. Do not retry."
    );
  }

  // Policy 1: Gate 2 must be recorded as approved in a gate ledger.
  const ledgers = findFiles(cwd, ".gates.md");
  if (ledgers.length === 0) {
    decide(
      "deny",
      "Gate 2 not approved: no gate ledger found (expected specifications/<workshop>/.gates.md). " +
        "Create the ledger, complete Gates 0/1/1.5, and record explicit Gate 2 approval before pushing to Jira."
    );
  }

  const approved = ledgers.filter((path) => gate2Approved(readText(path)));
  if (approved.length === 0) {
    decide(
      "deny",
      `Gate 2 not approved: found ${ledgers.length} gate ledger(s) but none records Gate 2 as approved. ` +
        "Present the formatted tasks, get explicit user approval for the target Jira project, " +
        "record it in the ledger's Gate 2 row, then retry."
    );
  }

  allow();
}

try {
  main();
} catch (error) {
  decide("ask", `BA guard failed unexpectedly (${error && error.message}). Confirm this Jira write manually.`);
}
