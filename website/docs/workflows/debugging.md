---
title: Debugging
sidebar_label: Debugging
sidebar_position: 4
description: How a bug is fixed at its root cause — symptom, reproduction, a failing test, a causal chain with evidence, the reach of the fix, a minimal change and a regression guard — and when the work leaves for a plan instead.
sources:
  - plugins/tsh-product-engineering/skills/debugging-code/
  - plugins/tsh-product-engineering/skills/orchestrating-feature-implementation/SKILL.md
  - plugins/tsh-product-engineering/skills/creating-implementation-plans/references/plan-building-blocks.md
  - plugins/tsh-product-engineering/agents/software-engineer.md
sources_hash: "a5cd4ea276514b0c5216e8b4a887b99553c2eb1a527c6528a0f0de790f5bcea3"
---

# Debugging

**Plugin:** [`tsh-product-engineering`](/docs/plugins/tsh-product-engineering/) · **Start with:** `/tsh-product-engineering:debugging-code`, or paste the stack trace, the failing test or the bug ticket — [`debugging-code`](/docs/plugins/tsh-product-engineering/skills/debugging-code) loads when code behaves wrongly and the cause is not yet known.

A bug is fixed when its cause is named, removed, and guarded by a test that failed before the fix and passes after it. Each step produces the evidence the next one needs: no reproduction, no trustworthy test; no failing test, no proof the fix did anything; no known cause, no way to tell how far the fix reaches.

A project's own incident runbook, bug-fix workflow or test conventions outrank the skill; it fills what they leave unstated. The project's test, lint and build commands are found the way [`discovering-technical-context`](/docs/plugins/tsh-product-engineering/skills/discovering-technical-context) finds them, not guessed.

## At a glance

<!-- PHASE2(visual): the procedure is a plain-text block because @docusaurus/theme-mermaid is not installed — the old site drew its workflows as diagrams — decide in Phase 2 whether to add the Mermaid theme or a diagram component -->

```text
1 pin the symptom ─▶ 2 reproduce ─▶ 3 failing test ─▶ 4 root cause
   ─▶ 5 reach of the fix ─┬─ local or shared, verifiable ─▶ 6 minimal fix ─▶ 7 verify ─▶ 8 siblings ─▶ 9 report
                          └─ design decision, contract others depend on, or unverifiable reach
                                ─▶ creating-implementation-plans, with the root cause in Technical Context
```

## Who runs it

| Situation | Runs in |
| :-- | :-- |
| You report a bug | The main conversation, with `debugging-code` |
| Feature implementation meets a bug whose cause is not established | The main conversation — [`orchestrating-feature-implementation`](/docs/plugins/tsh-product-engineering/skills/orchestrating-feature-implementation) routes it to `debugging-code` |
| A delegated fix for a reported failure — a review or verification finding, a failing test, a stack trace | [`software-engineer`](/docs/plugins/tsh-product-engineering/agents/software-engineer), which preloads `debugging-code` |

The subagent works under tighter limits. It cannot ask the user anything, so every step that needs a symptom it was not given, the user's agreement or a plan — and a failure it cannot reproduce — is a deviation it reports. It never runs `git bisect`, because bisect checks out other commits in a tree other agents may be editing; it reports the last good and first bad commit, and the main conversation runs the bisect. Its reach assessment stays inside the delegated scope. It returns the step 9 report block in full.

## Step by step

1. **Pin the symptom.** Expected versus actual behaviour, the exact error and stack trace, the environment and commit, since when and how often — pulled from the ticket, logs and `git log`; the user is asked only for what cannot be recovered. Then classify it: a defect in code follows the full procedure; a missing feature leaves for a plan; a configuration or data problem goes its own way; a wrong test is corrected in step 3 and the procedure skips to the report.
2. **Reproduce.** The smallest reliable trigger, recorded as a command or numbered steps, plus the last known good commit if there is one. A failure that will not reproduce stays open: the report lists what was tried and which evidence would unblock it.
3. **Secure a failing test**, in this order of preference: a test that already fails for the reported reason; an existing test corrected or extended to cover the case; a new test at the lowest layer that shows the bug, beside the module's existing tests. It must fail **for the reported reason** — failing on setup or another assertion proves nothing. Only when no test layer can exercise the fault is a manual reproduction recorded instead, and the guard is called partial.
4. **Find the root cause.** One hypothesis at a time, each with a check that could disprove it, kept in a hypothesis log when the first one fails. Techniques: bisect against the repro test in a throwaway worktree, shrinking the input, temporary instrumentation marked for removal. The result is a causal chain — trigger → faulty code at `file:line` → observed symptom — with evidence for each link.
5. **Assess the reach of the fix** before changing code: every call site (and any workaround that compensated for the bug), whether anything observable outside the module changes, and whether wrong data was written while the bug lived. Local means verify as written; shared or contract-changing widens verification to the callers' suites and the relevant E2E.
6. **Apply the minimal fix** at the cause — no refactoring, renaming or cleanup in the same change.
7. **Verify.** The step 3 test passes; the touched module's tests, and every caller's where step 5 found them, still pass; lint and typecheck are clean; the original reproduction no longer fails. All temporary instrumentation is removed.
8. **Look for siblings** — the same faulty pattern elsewhere, reported with `file:line`.
9. **Report**, in a fixed block:

```text
Symptom:       <expected vs actual, where, since when>
Reproduction:  <command or steps>
Root cause:    <trigger → file:line → symptom, with the evidence for each link>
Reach:         <local | shared, N callers | contract change — what others now observe differently>
Fix:           <files changed, one line on what changed and why it removes the cause>
Regression:    <test name and path; existing, corrected or new — failed before, passes after>
Verified:      <commands run and their results>
Siblings:      <file:line list, or "none found">
Open:          <mitigation-only status, residual risk, follow-ups — or "none">
```

## What the skill refuses to do

- **Fix at the symptom site** when the cause is elsewhere — a null guard, a swallowed exception, a retry, a longer timeout, a special case for the reported input. When the cause is genuinely out of reach, the change is labelled a **mitigation**, the open cause is named, and the user agrees to it.
- **Weaken, skip or delete a test** to make it pass, or change an expected value — unless the test itself is shown to be wrong, which the report then says.
- **Mutate production data or state.** Production logs, metrics and databases are read-only evidence.
- **Guess past the evidence.** After three rejected hypotheses in a row, when the evidence points into a third-party library, or when confirming a hypothesis needs production access, it escalates to the user with the hypothesis log.

## When the work leaves this workflow

| Finding | Goes to |
| :-- | :-- |
| The fix needs a design decision, changes a contract others depend on, or reaches further than can be verified | [`creating-implementation-plans`](/docs/plugins/tsh-product-engineering/skills/creating-implementation-plans): the causal chain and its evidence, plus the measured reach, go into the plan's Technical Context, so implementers fix that cause instead of re-investigating it. The plan is then run as [feature implementation](./feature-implementation) |
| The "bug" is a missing feature or a changed requirement | `creating-implementation-plans` — the skill says so and stops |
| A flaky end-to-end suite | The `tsh-product-testing` plugin. A flaky unit or integration test caused by application code stays in scope |
| A pipeline, cluster or cloud resource fault | The `tsh-platform-engineering` plugin — the gap is named to the user |
| The fix is ready for merge | [`reviewing-code`](/docs/plugins/tsh-product-engineering/skills/reviewing-code) judges it |

## Where people decide

| Point | What the user decides |
| :-- | :-- |
| Symptom | Supplies what the ticket, logs and history do not |
| Live outage | Agrees to reverting the offending commit as a labelled first mitigation; the procedure then runs against the reverted change |
| Mitigation | Agrees to a change that does not remove the cause |
| No reproduction | Agrees, or not, to shipping targeted permanent observability as its own change |
| Siblings | Agrees to each sibling fix, made as a separate change |
| Escalation | Receives the hypothesis log when the search stops narrowing |

## What it leaves behind

The fix, and the regression test beside the module's existing tests — corrected, extended or new — which failed before the fix and passes after it. The step 9 report states the rest. The skill defines no artifact file of its own; a fix that outgrows it continues in a plan file.
