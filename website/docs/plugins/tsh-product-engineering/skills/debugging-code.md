---
title: Debugging Code
sidebar_label: debugging-code
sidebar_position: 3
description: Finds and fixes the root cause of a bug by reproducing it, securing a failing test, naming the causal chain with evidence and measuring the reach of the fix before applying it minimally.
sources:
  - plugins/tsh-product-engineering/skills/debugging-code/
sources_hash: "dbe72ec3867e5107adc23790a31e6416e4bfb6cf2bb2838784dfbace1e6cb666"
---

# Debugging Code

**Plugin:** [`tsh-product-engineering`](/docs/plugins/tsh-product-engineering/)  
**Invoke:** `/tsh-product-engineering:debugging-code`  
**Used by:** the [`software-engineer`](/docs/plugins/tsh-product-engineering/agents/software-engineer) agent preloads it. [`orchestrating-feature-implementation`](/docs/plugins/tsh-product-engineering/skills/orchestrating-feature-implementation) routes a bug whose cause is not yet established to it, and [`creating-implementation-plans`](/docs/plugins/tsh-product-engineering/skills/creating-implementation-plans) takes over from it when a fix outgrows a minimal change.

A bug is fixed when its cause is named, removed and guarded by a test that failed before the fix and passes after it. Anything else is a guess that happened to make the symptom go away. Each step produces the evidence the next one needs: no reproduction means no trustworthy test, no failing test means no proof the fix did anything, and no known cause means no way to tell how far the fix reaches.

Use it when code behaves wrongly and the cause is not yet known: a pasted stack trace, a test that started failing, a regression after a merge or dependency upgrade, or a bug ticket. Load it before reading, searching or editing the code, because locating the cause is the skill's own first step. The skill takes the bug description as its argument and asks for the symptom if none is given. A project's own incident runbook or bug-fix workflow outranks it.

## Key Areas

| Area | Coverage |
| :-- | :-- |
| **Reproduce first** | The failure is reproduced before any code changes. A bug that cannot be reproduced stays open, with a report of what was tried and what evidence would unblock it |
| **Failing test** | A failing automated test is required before fixing, in this order of preference: one that already fails for this reason, an existing test corrected or extended, or a new test at the lowest layer that exhibits the bug. It must fail for the reported reason |
| **Root cause as a causal chain** | Trigger, faulty code at `file:line`, and observed symptom, with evidence for each link. "This looks wrong" is a hypothesis, not a cause |
| **No symptom-site fixes** | No null guard, swallowed exception, retry, longer timeout or special case for the reported input when the cause is elsewhere. If the cause is genuinely out of reach, the change is labeled a mitigation, the open cause is named, and the user agrees |
| **Minimal fix** | Only what the root cause requires, with no refactoring or unrelated cleanup |
| **Tests stay honest** | A test is never weakened, skipped or deleted to make it pass, nor an expected value changed, unless the test is shown to be wrong, and then the report says so |
| **Reach assessment** | Before changing code: how many call sites the faulty code has, whether the fix changes anything observable outside the module, and whether wrong data was written while the bug lived |
| **Stop and plan** | A fix that needs a design decision, changes a contract others depend on, or reaches further than can be verified moves to `creating-implementation-plans` with the established root cause |
| **Read-only production** | Production logs, metrics and databases are evidence only. Nothing in production is mutated while investigating |

## Explicit exclusions

- **New behavior.** A "bug" that turns out to be a missing feature or changed requirement goes to `creating-implementation-plans`.
- **Flaky end-to-end suites.** Test-infrastructure stability belongs to the `tsh-product-testing` plugin. A flaky unit or integration test whose cause is in application code is in scope.
- **Infrastructure and deployment faults.** A misconfigured pipeline, cluster or cloud resource belongs to `tsh-platform-engineering`. The skill names the gap to the user.

## How it works

1. **Pin the symptom.** Expected versus actual behavior, the exact error and stack trace, environment and commit, since when and how often, pulled from the ticket, logs and `git log` before asking the user. Then assess whether it is a code defect, a configuration or data problem, a missing feature or a wrong test. Only a code defect follows the full procedure.
2. **Reproduce.** Find the smallest reliable trigger and record it as a command or numbered steps, noting the last known good commit when there is one.
3. **Secure a failing test.** Look for an existing failing or incorrect test before writing a new one, and run it to confirm the failure matches the symptom.
4. **Find the root cause.** One hypothesis at a time, each tested with a check that could disprove it, finishing with the causal chain.
5. **Assess the reach of the fix.** Callers, contract and data.
6. **Apply the minimal fix** at the cause.
7. **Verify.** The step 3 test passes, the touched module's and every caller's tests still pass, lint and typecheck are clean, the original reproduction no longer fails, and temporary instrumentation is removed.
8. **Look for siblings.** The same faulty pattern elsewhere is reported with `file:line` and fixed only with the user's agreement, as separate changes.
9. **Report** in a fixed block: Symptom, Reproduction, Root cause, Reach, Fix, Regression, Verified, Siblings and Open.

During a live outage, reverting the offending commit is a legitimate first mitigation. It is labeled as such, needs the user's agreement, and the procedure then runs against the reverted change so the cause is found before it ships again.

## Reference Loading

| Reference | Load when | Covers |
| :-- | :-- | :-- |
| `reproducing-failures.md` | The bug does not reproduce on the first attempt, reproduces only in one environment, or it is unclear which test layer can express it | Closing the environment gap, data-dependent and timing-dependent bugs, choosing the test layer, what to do when no automated test can capture it, and what to report when it does not reproduce at all |
| `root-cause-techniques.md` | The first hypothesis fails, or the stack trace does not point at the faulty line | The hypothesis log, `git bisect run` with the repro test in a throwaway worktree, shrinking the input, temporary instrumentation, misleading stack traces, concurrency and shared-state bugs, and when to stop and ask |

A delegated implementer does not bisect. When a bisect is called for, it reports the last known good and the first bad commit, and the main conversation runs the bisect.

## Related skills

- [`discovering-technical-context`](/docs/plugins/tsh-product-engineering/skills/discovering-technical-context) supplies the project's test, lint and build commands.
- [`creating-implementation-plans`](/docs/plugins/tsh-product-engineering/skills/creating-implementation-plans) takes over when the fix outgrows a minimal change.
- [`reviewing-code`](/docs/plugins/tsh-product-engineering/skills/reviewing-code) judges the fix before merge.

For the end-to-end picture see the [debugging workflow](/docs/workflows/debugging).

## Source

[`plugins/tsh-product-engineering/skills/debugging-code/SKILL.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-product-engineering/skills/debugging-code/SKILL.md)
