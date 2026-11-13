// Tests for the tsh-product-management Jira write guard (a PreToolUse hook).
//
//     node --test tests/jira-write-guard/guard-jira-write.test.mjs
//
// Each test spawns the real hook with a PreToolUse payload on stdin, in a throwaway directory
// that holds (or lacks) the Business Analysis artifacts the hook looks for. There is no
// network and no Jira: the hook only reads files under the payload's `cwd`.
//
// One test per row of the payload table in the migration plan. "silent" is the hook allowing
// the call (exit 0, empty stdout); `deny` and `ask` are JSON decisions on stdout.
import { test, before, after } from "node:test";
import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { mkdirSync, mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

const HOOK = fileURLToPath(
  new URL("../../plugins/tsh-product-management/hooks/guard-jira-write.mjs", import.meta.url),
);

const JIRA_TASKS = `# Jira Tasks — w1

### Story 1.4: Import invoices 🔒

**Parent**: Billing
**Jira Key**: ACME-441
**Status**: Done

---

### Story 1.5: Export invoices

**Parent**: Billing
**Jira Key**: ACME-5
**Status**: To Do
`;

const gateLedger = (gate2) => `# Gate Ledger — w1

| Gate | Artifact | Status | Approved at |
|---|---|---|---|
| 0 | intent-brief.md | approved | 2026-11-01 |
| 1 | extracted-tasks.md | approved | 2026-11-01 |
| 1.5 | quality-review.md | approved | 2026-11-01 |
| 1.75 | .roadmap-proposal.md | approved | 2026-11-01 |
${gate2}
`;

const GATES_APPROVED = gateLedger("| 2 | jira-tasks.md | approved | 2026-11-13 10:00 — project ACME, batch push |");
const GATES_PENDING = gateLedger("| 2 | jira-tasks.md | pending | — |");

// One protection trigger per block, so each is proven on its own.
const JIRA_TASKS_POLICY = `# Jira Tasks — w1

### Story 2.1: Lock only 🔒

**Jira Key**: ACME-441
**Status**: To Do

---

### Story 2.2: Cancelled

**Jira Key**: ACME-442
**Status**: Cancelled

---

### Story 2.3: PO approved

**Jira Key**: ACME-443
**Status**: PO APPROVE

---

### Story 2.4: Done without lock

**Jira Key**: ACME-444
**Status**: Done

---

### Story 2.5: Open

**Jira Key**: ACME-5
**Status**: To Do
`;

let root;
const fixtures = {};

function write(dir, relativePath, content) {
  const full = path.join(dir, relativePath);
  mkdirSync(path.dirname(full), { recursive: true });
  writeFileSync(full, content);
}

before(() => {
  root = mkdtempSync(path.join(tmpdir(), "jira-guard-"));
  const make = (name, files) => {
    fixtures[name] = path.join(root, name);
    mkdirSync(fixtures[name]);
    for (const [relativePath, content] of Object.entries(files)) write(fixtures[name], relativePath, content);
  };
  const w1 = "specifications/w1";
  const archived = "specifications/projects/p/sessions/2026-11-01-w0";
  make("A", {}); // no BA session: the guard stands down
  make("B", { [`${w1}/jira-tasks.md`]: JIRA_TASKS }); // BA session, no ledger
  make("C", { [`${w1}/.gates.md`]: GATES_APPROVED }); // approved for ACME, nothing protected
  make("D", { [`${w1}/jira-tasks.md`]: JIRA_TASKS, [`${w1}/.gates.md`]: GATES_APPROVED });
  make("S", { [`${archived}/jira-tasks.md`]: JIRA_TASKS, [`${archived}/.gates.md`]: GATES_APPROVED });
  make("P", { [`${w1}/jira-tasks.md`]: JIRA_TASKS_POLICY, [`${w1}/.gates.md`]: GATES_APPROVED });
  make("U", { [`${w1}/jira-tasks.md`]: JIRA_TASKS, [`${w1}/.gates.md`]: GATES_PENDING });
});

after(() => {
  if (root) rmSync(root, { recursive: true, force: true });
});

const atlassian = (tool) => `mcp__plugin_tsh-core_atlassian__${tool}`;
const exec = (name, inputs) => ({ name, cloudId: "c", inputs });
const execWithoutName = (inputs) => ({ cloudId: "c", inputs });

/** Runs the hook with `input` on stdin in fixture `dir`. */
function spawnHook(dir, input) {
  return spawnSync(process.execPath, [HOOK], { input, cwd: fixtures[dir], encoding: "utf8" });
}

function runHook(dir, toolName, toolInput) {
  const payload = { hook_event_name: "PreToolUse", tool_name: toolName, tool_input: toolInput, cwd: fixtures[dir] };
  return spawnHook(dir, JSON.stringify(payload));
}

function assertSilent(result) {
  assert.equal(result.status, 0, result.stderr);
  assert.equal(result.stdout, "", "expected the hook to stay silent");
}

function assertDecision(result, decision, fragments) {
  assert.equal(result.status, 0, result.stderr);
  assert.notEqual(result.stdout, "", `expected ${decision}, but the hook stayed silent`);
  const output = JSON.parse(result.stdout).hookSpecificOutput;
  assert.equal(output.permissionDecision, decision, output.permissionDecisionReason);
  for (const fragment of fragments) {
    assert.ok(
      output.permissionDecisionReason.includes(fragment),
      `reason does not contain ${JSON.stringify(fragment)}: ${output.permissionDecisionReason}`,
    );
  }
}

const silent = { decision: null, fragments: [] };
const deny = (...fragments) => ({ decision: "deny", fragments });
const ask = (...fragments) => ({ decision: "ask", fragments });

/** One row of the payload table: one test. */
function row(number, dir, title, toolName, toolInput, expected) {
  test(`${number} ${dir} ${title}`, () => {
    const result = runHook(dir, toolName, toolInput);
    if (expected.decision === null) assertSilent(result);
    else assertDecision(result, expected.decision, expected.fragments);
  });
}

const GATE2 = "Gate 2 not approved";
const OTHER = "does not cover project OTHER";
const PROTECTED = (key) => `Protected Status Policy: ${key}`;
const UNCLASSIFIED = (runner) => `could not classify "${runner}`;

// Nested reference: the linked issue sits in `fields.issuelinks[0].outwardIssue.key`.
const nested = (key) => ({ issueIdOrKey: "ACME-5", fields: { issuelinks: [{ outwardIssue: { key } }] } });

row(1, "A", "executeWrite → createJiraIssue", atlassian("executeWrite"), exec("createJiraIssue", { projectKey: "ACME" }), silent);
row(2, "B", "discover", atlassian("discover"), { query: "create a jira issue" }, silent);
row(3, "B", "executeRead → getJiraIssue", atlassian("executeRead"), exec("getJiraIssue", { issueIdOrKey: "ACME-1" }), silent);
row(4, "D", "executeRead → listJiraIssueTransitions", atlassian("executeRead"), exec("listJiraIssueTransitions", { issueIdOrKey: "ACME-441" }), silent);
row(5, "B", "executeRead → editJiraIssue", atlassian("executeRead"), exec("editJiraIssue", { issueIdOrKey: "ACME-1" }), deny(GATE2));
row(6, "B", "executeWrite → createJiraIssue", atlassian("executeWrite"), exec("createJiraIssue", { projectKey: "ACME" }), deny(GATE2));
row(7, "C", "executeWrite → createJiraIssue", atlassian("executeWrite"), exec("createJiraIssue", { projectKey: "ACME" }), silent);
row(8, "D", "executeWrite → createJiraIssue", atlassian("executeWrite"), exec("createJiraIssue", { projectKey: "OTHER" }), deny(OTHER));
row(9, "D", "executeWrite → editJiraIssue", atlassian("executeWrite"), exec("editJiraIssue", { issueIdOrKey: "ACME-441" }), deny(PROTECTED("ACME-441")));
row(
  10, "D", "executeWrite → createJiraIssueLink", atlassian("executeWrite"),
  exec("createJiraIssueLink", { inwardIssue: "ACME-441", outwardIssue: "ACME-5", linkType: "Blocks" }),
  deny(PROTECTED("ACME-441")),
);
row(
  11, "D", "executeWrite → createJiraIssueLink", atlassian("executeWrite"),
  exec("createJiraIssueLink", { inwardIssue: "OTHER-1", outwardIssue: "ACME-5" }),
  deny(OTHER),
);
row(
  12, "C", "executeWrite → createJiraIssueLink", atlassian("executeWrite"),
  exec("createJiraIssueLink", { inwardIssue: "ACME-5", outwardIssue: "ACME-6" }),
  silent,
);
row(13, "D", "createIssueLink", atlassian("createIssueLink"), { inwardIssue: "ACME-441", outwardIssue: "ACME-5" }, deny(PROTECTED("ACME-441")));
row(14, "B", "executeDestructive → deleteJiraIssue", atlassian("executeDestructive"), exec("deleteJiraIssue", { issueIdOrKey: "ACME-2" }), deny(GATE2));
row(15, "C", "executeDestructive → deleteJiraIssue", atlassian("executeDestructive"), exec("deleteJiraIssue", { issueIdOrKey: "ACME-2" }), silent);
row(16, "B", "executeWrite → updateConfluenceContent", atlassian("executeWrite"), exec("updateConfluenceContent", { contentId: "123", body: "x" }), silent);
row(17, "B", "executeDestructive → deleteConfluenceContent", atlassian("executeDestructive"), exec("deleteConfluenceContent", { contentId: "123" }), silent);
row(
  18, "B", "executeWrite → mergeBitbucketRepoPullRequest", atlassian("executeWrite"),
  exec("mergeBitbucketRepoPullRequest", { workspace: "w", repoSlug: "r", pullRequestId: 1 }),
  silent,
);
row(
  19, "B", "executeWrite → createCompassComponent", atlassian("executeWrite"),
  exec("createCompassComponent", { name: "svc" }),
  ask("could not classify", "createCompassComponent"),
);
row(20, "B", "executeWrite (no name)", atlassian("executeWrite"), execWithoutName({ projectKey: "ACME" }), ask(UNCLASSIFIED("executeWrite")));
row(21, "B", "executeWrite → linkJiraIssueToConfluencePage", atlassian("executeWrite"), exec("linkJiraIssueToConfluencePage", { issueIdOrKey: "ACME-1" }), deny(GATE2));
row(22, "B", "mcp__claude_ai_Atlassian__executeWrite → createJiraIssue", "mcp__claude_ai_Atlassian__executeWrite", exec("createJiraIssue", { projectKey: "ACME" }), deny(GATE2));
row(23, "D", "editJiraIssue", atlassian("editJiraIssue"), { issueIdOrKey: "ACME-441" }, deny(PROTECTED("ACME-441")));
row(24, "D", "createJiraIssue", atlassian("createJiraIssue"), { projectKey: "OTHER" }, deny(OTHER));
row(25, "C", "editJiraIssue", atlassian("editJiraIssue"), { issueIdOrKey: "ACME-5" }, silent);
row(26, "B", "addOrEditJiraIssueComment", atlassian("addOrEditJiraIssueComment"), { issueIdOrKey: "ACME-1" }, deny(GATE2));
row(27, "B", "transitionJiraIssue", atlassian("transitionJiraIssue"), { issueIdOrKey: "ACME-1" }, deny(GATE2));
row(28, "B", "listJiraIssueComments", atlassian("listJiraIssueComments"), { issueIdOrKey: "ACME-1" }, silent);

test("29 B getConfluenceContent, createConfluenceContent", () => {
  assertSilent(runHook("B", atlassian("getConfluenceContent"), { contentId: "123" }));
  assertSilent(runHook("B", atlassian("createConfluenceContent"), { contentId: "123" }));
});

row(30, "B", "manageJiraSprint", atlassian("manageJiraSprint"), { sprintId: 1 }, ask("could not classify"));
row(31, "S", "editJiraIssue", atlassian("editJiraIssue"), { issueIdOrKey: "ACME-441" }, silent);
row(32, "B", "mcp__github__create_issue", "mcp__github__create_issue", { title: "x" }, silent);

test("33 B stdin not json", () => {
  assertDecision(spawnHook("B", "not json"), "ask", ["could not parse"]);
});

// Malformed operation names — never an early allow, on any runner.
const projectInputs = { projectKey: "ACME" };
const readInputs = { issueIdOrKey: "ACME-1" };
row(34, "B", 'executeWrite, name ""', atlassian("executeWrite"), exec("", projectInputs), ask(UNCLASSIFIED("executeWrite")));
row(35, "B", 'executeWrite, name "   "', atlassian("executeWrite"), exec("   ", projectInputs), ask(UNCLASSIFIED("executeWrite")));
row(36, "B", "executeWrite, name null", atlassian("executeWrite"), exec(null, projectInputs), ask(UNCLASSIFIED("executeWrite")));
row(37, "B", "executeWrite, name 42", atlassian("executeWrite"), exec(42, projectInputs), ask(UNCLASSIFIED("executeWrite")));
row(38, "B", "executeWrite, name {op}", atlassian("executeWrite"), exec({ op: "createJiraIssue" }, projectInputs), ask(UNCLASSIFIED("executeWrite")));
row(39, "B", "executeRead (no name)", atlassian("executeRead"), execWithoutName(readInputs), ask(UNCLASSIFIED("executeRead")));
row(40, "B", "executeRead, name 42", atlassian("executeRead"), exec(42, readInputs), ask(UNCLASSIFIED("executeRead")));
row(41, "B", "executeDestructive (no name)", atlassian("executeDestructive"), execWithoutName({ issueIdOrKey: "ACME-2" }), ask(UNCLASSIFIED("executeDestructive")));

// Prefixes, case and mixed products — Jira wins.
row(42, "B", "executeWrite → jira_edit_issue", atlassian("executeWrite"), exec("jira_edit_issue", readInputs), deny(GATE2));
row(43, "B", "executeWrite → confluence_update_page", atlassian("executeWrite"), exec("confluence_update_page", { pageId: "123" }), silent);
row(44, "B", "executeWrite → jira_edit_bitbucket_issue", atlassian("executeWrite"), exec("jira_edit_bitbucket_issue", readInputs), deny(GATE2));
row(45, "B", "executeDestructive → JiRa_deleteConfluenceContent", atlassian("executeDestructive"), exec("JiRa_deleteConfluenceContent", { contentId: "123" }), deny(GATE2));
row(46, "B", "executeWrite → linkBitbucketPullRequestToJiraIssue", atlassian("executeWrite"), exec("linkBitbucketPullRequestToJiraIssue", readInputs), deny(GATE2));
row(47, "B", 'executeWrite → "  createJiraIssue  "', atlassian("executeWrite"), exec("  createJiraIssue  ", projectInputs), deny(GATE2));

// executeRead: valid reads pass, write-verb names are gated.
row(48, "B", 'executeRead → " editJiraIssue "', atlassian("executeRead"), exec(" editJiraIssue ", readInputs), deny(GATE2));
row(49, "B", "executeRead → jira_edit_issue", atlassian("executeRead"), exec("jira_edit_issue", readInputs), deny(GATE2));
row(50, "B", "executeRead → jira_get_issue", atlassian("executeRead"), exec("jira_get_issue", readInputs), silent);
row(51, "B", "executeRead → updateConfluenceContent", atlassian("executeRead"), exec("updateConfluenceContent", { contentId: "123" }), silent);
row(
  52, "B", "executeRead → createCompassComponent", atlassian("executeRead"),
  exec("createCompassComponent", { name: "svc" }),
  ask("could not classify", "createCompassComponent"),
);
row(53, "B", "executeRead → listJiraIssueTransitions", atlassian("executeRead"), exec("listJiraIssueTransitions", readInputs), silent);
row(54, "B", "executeRead → listJiraIssueComments", atlassian("executeRead"), exec("listJiraIssueComments", readInputs), silent);
row(55, "B", "executeRead → searchJiraIssuesUsingJql", atlassian("executeRead"), exec("searchJiraIssuesUsingJql", { jql: "project = ACME" }), silent);

// Nested references: a primary call and the same call wrapped in a runner must agree.
row(56, "D", "editJiraIssue N(ACME-441)", atlassian("editJiraIssue"), nested("ACME-441"), deny(PROTECTED("ACME-441")));
row(57, "D", "executeWrite → editJiraIssue N(ACME-441)", atlassian("executeWrite"), exec("editJiraIssue", nested("ACME-441")), deny(PROTECTED("ACME-441")));
row(58, "D", "editJiraIssue N(OTHER-1)", atlassian("editJiraIssue"), nested("OTHER-1"), deny(OTHER));
row(59, "D", "executeWrite → editJiraIssue N(OTHER-1)", atlassian("executeWrite"), exec("editJiraIssue", nested("OTHER-1")), deny(OTHER));

// executeDestructive: protection and project scope.
row(60, "D", "executeDestructive → deleteJiraIssue ACME-441", atlassian("executeDestructive"), exec("deleteJiraIssue", { issueIdOrKey: "ACME-441" }), deny(PROTECTED("ACME-441")));
row(61, "D", "executeDestructive → deleteJiraIssue OTHER-2", atlassian("executeDestructive"), exec("deleteJiraIssue", { issueIdOrKey: "OTHER-2" }), deny(OTHER));

// Each protection trigger on its own.
row(62, "P", "editJiraIssue ACME-441 (lock only)", atlassian("editJiraIssue"), { issueIdOrKey: "ACME-441" }, deny(PROTECTED("ACME-441")));
row(63, "P", "executeWrite → editJiraIssue ACME-442 (Cancelled)", atlassian("executeWrite"), exec("editJiraIssue", { issueIdOrKey: "ACME-442" }), deny(PROTECTED("ACME-442")));
row(64, "P", "executeWrite → editJiraIssue ACME-443 (PO APPROVE)", atlassian("executeWrite"), exec("editJiraIssue", { issueIdOrKey: "ACME-443" }), deny(PROTECTED("ACME-443")));
row(65, "P", "executeWrite → editJiraIssue ACME-444 (Done)", atlassian("executeWrite"), exec("editJiraIssue", { issueIdOrKey: "ACME-444" }), deny(PROTECTED("ACME-444")));
row(66, "P", "executeWrite → editJiraIssue ACME-5", atlassian("executeWrite"), exec("editJiraIssue", { issueIdOrKey: "ACME-5" }), silent);

// Ledger present, Gate 2 pending.
row(67, "U", "executeWrite → createJiraIssue", atlassian("executeWrite"), exec("createJiraIssue", projectInputs), deny("none records Gate 2 as approved"));
row(68, "U", "createJiraIssue", atlassian("createJiraIssue"), projectInputs, deny("none records Gate 2 as approved"));
row(69, "U", "executeRead → getJiraIssue", atlassian("executeRead"), exec("getJiraIssue", readInputs), silent);

// `discover` and the runners match the tool name as sent: a product prefix makes it another tool.
row(70, "B", "mcp__atlassian__jira_discover", "mcp__atlassian__jira_discover", readInputs, ask("could not classify"));
row(
  71, "B", "mcp__jira__jira_executeRead → doSomething", "mcp__jira__jira_executeRead",
  exec("doSomething", readInputs),
  ask("could not classify"),
);
