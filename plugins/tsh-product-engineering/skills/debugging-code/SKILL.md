---
name: debugging-code
description: "Finds and fixes the root cause of a bug: pins the symptom, reproduces it, secures a failing test — existing, corrected or new — narrows to the cause with evidence rather than plausibility, measures how far the fix reaches before applying it minimally, and keeps the test as a regression guard. Use when code behaves wrongly and the cause is not yet known — before editing anything."
when_to_use: "Trigger on: 'fix this bug', 'why does this fail', 'this throws', a pasted stack trace or error log, a test that started failing, a regression after a merge, deploy or dependency upgrade, 'it worked yesterday', a production error that needs a code fix, or a bug ticket. Building new behaviour is orchestrating-feature-implementation; judging a finished fix is reviewing-code."
---

# Debugging Code

A bug is fixed when its cause is named, removed, and guarded by a test that failed
before the fix and passes after it; anything else is a guess that happened to make
the symptom go away. Each step produces the evidence the next one needs: no
reproduction, no trustworthy test; no failing test, no proof the fix did anything;
no known cause, no way to tell how far the fix reaches.

Investigate the bug in `$ARGUMENTS`; if empty, ask for the symptom before reading code.

## Applicability and Precedence

A project's own incident runbook, bug-fix workflow or test conventions outrank this
skill — follow them and use this procedure for what they leave unstated. Find the
project's test, lint and build commands the way
[`discovering-technical-context`](../discovering-technical-context/SKILL.md) does,
not by guessing.

## Explicit Exclusions

- **New behaviour** — a "bug" that turns out to be a missing feature or a changed
  requirement goes to [`creating-implementation-plans`](../creating-implementation-plans/SKILL.md).
  Say so and stop; do not build it under the name of a fix.
- **Flaky end-to-end suites** — test-infrastructure stability belongs to the
  `tsh-product-testing` plugin. A flaky *unit or integration* test whose cause is in
  application code is in scope.
- **Infrastructure and deployment faults** — a misconfigured pipeline, cluster or
  cloud resource belongs to `tsh-platform-engineering`. Name the gap to the user.

## Non-negotiable Rules

| Severity | Rule |
| --- | --- |
| MUST | Reproduce the failure before changing any code. A bug you cannot reproduce stays open: report what was tried and what evidence would unblock it — never ship a speculative fix as a fix. |
| MUST | Have a failing automated test before fixing — one that already fails for this reason, an existing test corrected or extended to cover the case, or a new one at the lowest layer that exhibits the bug, in that order of preference. Watch it fail **for the reported reason**: a test that fails on setup, or on a different assertion, proves nothing. Only when no test layer in the project can exercise the fault, record the manual reproduction instead and say the guard is partial. |
| MUST | State the root cause as a causal chain — trigger → faulty code at `file:line` → observed symptom — with the evidence for each link: an observed value, a log line, a bisect result. "This looks wrong" is a hypothesis, not a cause. |
| NEVER | Fix at the symptom site when the cause is elsewhere: a null guard, a swallowed exception, a retry, a longer timeout, or a special case for the reported input. If the cause is genuinely out of reach, label the change a **mitigation**, name the open cause, and get the user's agreement. |
| MUST | Keep the fix minimal — only what the root cause requires. No refactoring, renaming or unrelated cleanup in the same change. |
| NEVER | Weaken, skip or delete a test to make it pass, or change an expected value, unless the test itself is shown to be wrong — and then say so explicitly in the report. |
| MUST | Assess the reach of the fix once the cause is known and before changing code — how many call sites the faulty code has, and whether the fix changes anything observable outside the module. Verification scales with the answer; a fix is never "simple" by the look of the symptom. |
| MUST | Stop and move to a plan when the fix needs a design decision, changes a contract others depend on, or reaches further than you can verify: hand the established root cause to `creating-implementation-plans` so it lands in the plan's Technical Context. |
| NEVER | Mutate production data or state while investigating. Production logs, metrics and databases are read-only evidence. |

## Reference Loading

| Reference | Load when | Covers |
| --- | --- | --- |
| [Reproducing failures](./references/reproducing-failures.md) | The bug does not reproduce on the first attempt, reproduces only in one environment, or it is unclear which test layer can express it | Narrowing the environment gap, data- and timing-dependent bugs, choosing the test layer, what to do when no automated test can capture it |
| [Root-cause techniques](./references/root-cause-techniques.md) | The first hypothesis fails, or the stack trace does not point at the faulty line | The hypothesis log, `git bisect run` with the repro test, shrinking the input, temporary instrumentation, async and minified stack traces, concurrency bugs |

## Procedure

Copy this checklist and track progress:

```text
Debugging progress:
- [ ] 1. Pin the symptom
- [ ] 2. Reproduce
- [ ] 3. Secure a failing test
- [ ] 4. Find the root cause
- [ ] 5. Assess the reach of the fix
- [ ] 6. Apply the minimal fix
- [ ] 7. Verify
- [ ] 8. Look for siblings
- [ ] 9. Report
```

**Step 1 — Pin the symptom.** Write down expected versus actual behaviour, the exact
error and stack trace, the environment and commit where it happens, since when, and
how often. Pull what you can from the ticket, logs and `git log` yourself; ask the
user only for what is not recoverable. A vague symptom produces a vague fix.

Then assess what you are looking at before touching anything: a defect in code, a
configuration or data problem, a missing feature, or a test that is itself wrong.
Each goes a different way — only the first follows the full procedure below, a
missing feature leaves for a plan, and a wrong test is corrected in step 3, after
which the procedure skips to the report and says so. Note which test layers exist
for the affected module; that decides how step 3 can be satisfied.

A live outage changes the order, not the rules: reverting the offending commit is a
legitimate first mitigation — label it so, get the user's agreement, then run the
procedure against the reverted change so the cause is found before it ships again.

**Step 2 — Reproduce.** Find the smallest, most reliable way to trigger the failure
and record it as a command or a numbered list of steps. Note the last known good
commit if there is one — it bounds the search in step 4. If the failure does not
reproduce, read [`./references/reproducing-failures.md`](./references/reproducing-failures.md)
before trying anything else.

**Step 3 — Secure a failing test.** Look before writing:

1. A test already fails for the reported reason — that is the test; move on.
2. An existing test covers the path but asserts the buggy behaviour or misses the
   failing case — correct or extend it. Changing an expectation here is legitimate
   precisely because the test is shown to be wrong; name that in the report.
3. Nothing covers it — write a test at the lowest layer that shows the bug: unit if
   the fault is in pure logic, integration if it needs the real database, queue or
   service boundary. Put it beside the module's existing tests.
4. No test layer can exercise the fault — read §5 of
   [`./references/reproducing-failures.md`](./references/reproducing-failures.md).

Whichever applies, run it and confirm the failure message matches the symptom from
step 1.

**Step 4 — Find the root cause.** Form one hypothesis at a time and test it with a
check that could disprove it. Read the stack trace from the bottom of your own code,
not the top of the framework's. When the first hypothesis fails, read
[`./references/root-cause-techniques.md`](./references/root-cause-techniques.md) and
keep a hypothesis log. Finish with the causal chain the rules table demands.

**Step 5 — Assess the reach of the fix.** You now know which code will change;
measure what depends on it before changing it:

- **Callers.** Find every call site. One caller is a local fix. Many means every
  caller gets the new behaviour — read each for a workaround that compensated for
  the bug, because fixing the cause breaks the workaround.
- **Contract.** Does the fix change something observable outside the module —
  response shape, validation strictness, error type or status, persisted or
  serialized format, event payload, query semantics, ordering? That reaches clients
  and stored data, not only code.
- **Data.** Was wrong data written while the bug lived? Then the code fix is half
  the job; name the backfill or migration as a follow-up.

Local → step 7 as written. Shared or contract-changing → step 7 widens to the
callers' suites and the relevant e2e, and the report calls the change out. A
contract others depend on, or a reach you cannot verify → the plan rule applies.

**Step 6 — Apply the minimal fix.** Change the code at the cause, nothing more.

**Step 7 — Verify.** The test from step 3 now passes; the tests of the touched
module — and of every caller, where step 5 found them — still pass; lint and
typecheck are clean; the original reproduction from step 2 no longer fails. Remove
every piece of temporary instrumentation.

**Step 8 — Look for siblings.** Search for the same faulty pattern elsewhere — the
same misused API, the same unchecked assumption, the copy-pasted block. Report each
hit with `file:line`; fix them only with the user's agreement, as separate changes.

**Step 9 — Report.**

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

## Related Skills

Ship in this plugin — if this skill loaded, they are installed.
[`discovering-technical-context`](../discovering-technical-context/SKILL.md) supplies
the project's commands and conventions;
[`creating-implementation-plans`](../creating-implementation-plans/SKILL.md) takes
over when the fix outgrows a minimal change;
[`reviewing-code`](../reviewing-code/SKILL.md) judges the fix before merge.
