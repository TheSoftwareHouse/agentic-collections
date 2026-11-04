---
title: Reviewing UI
sidebar_label: reviewing-ui
sidebar_position: 7
description: Runs one UI verification pass against Figma by delegating fresh capture to ui-capture-worker and the design comparison to ui-reviewer, returning PASS, FAIL or VERIFICATION NOT RUN.
sources:
  - plugins/tsh-product-engineering/skills/reviewing-ui/
sources_hash: "4698690292ea9a372abc2b901c6f039cd3cdc944e09f96ccb807757ababae50e"
---

# Reviewing UI

**Plugin:** [`tsh-product-engineering`](/docs/plugins/tsh-product-engineering/)  
**Invoke:** `/tsh-product-engineering:reviewing-ui`  
**Used by:** [`orchestrating-feature-implementation`](/docs/plugins/tsh-product-engineering/skills/orchestrating-feature-implementation) repeats this pass inside its UI verification gate. It delegates to the agents [`ui-capture-worker`](/docs/plugins/tsh-product-engineering/agents/ui-capture-worker) and [`ui-reviewer`](/docs/plugins/tsh-product-engineering/agents/ui-reviewer), and can also be invoked standalone. The `tsh-stack-frontend` skill [`implementing-frontend`](/docs/plugins/tsh-stack-frontend/skills/implementing-frontend) points to it for UI verification against Figma.

One verification pass comparing the current implementation against its Figma design, run from the main conversation. The pass is delegate-only and read-only: capture belongs to the `ui-capture-worker` subagent, judgment to the `ui-reviewer` subagent, and no code changes happen here. The result is `PASS`, `FAIL` or `VERIFICATION NOT RUN`, with a complete difference table.

Use it to verify implemented UI against a Figma design, to check whether a page matches its design, or to re-verify a component after a fix. Judging code quality is [`reviewing-code`](/docs/plugins/tsh-product-engineering/skills/reviewing-code). During feature delivery the verify-fix loop in `orchestrating-feature-implementation` owns iteration budgets and escalation, and this skill is the single pass it repeats.

The skill takes from its arguments: the Figma URL (or pinned node link), the exact full dev server URL, the component or section name, and optionally a task ID or artifact directory. It asks the user for whatever is missing and never infers the dev server URL from config files, running processes or port scans.

## Key Areas

| Area | Coverage |
| :-- | :-- |
| **Pinned URL** | The user-confirmed full dev server URL is confirmed once, then forwarded unchanged to every capture and review delegation. Never rediscovered, normalized or port-swapped |
| **Delegate-only** | Capture goes to `ui-capture-worker`, judgment to `ui-reviewer`. Code review, type checks, builds and ad-hoc browser inspection never substitute for the delegated pass |
| **Hard ordering gate** | `ui-reviewer` is invoked only after a completed capture for the current iteration and when `actual.png`, `computed-styles.json` and `a11y-snapshot.yml` are confirmed present in the iteration directory |
| **Report contract** | The reviewer's report must contain `Verification Result`, `Component`, `Artifact Directory`, per-artifact status and blocker guidance. An invalid report is rerun once with a stricter handoff, then treated as `VERIFICATION NOT RUN` |
| **Saved report** | The reviewer is read-only, so the orchestrating conversation saves its report verbatim as `iteration-<N>/report.md` |
| **Blocker state** | `VERIFICATION NOT RUN` is never treated as PASS or FAIL. The blocker is resolved with the user, then capture and review rerun on fresh artifacts |
| **No auth bypass** | The skill never bypasses an authentication or access gate, never asks for credentials in chat and never lets a delegate do either. The default resolution is the repo-root `.env` contract the capture worker returns |
| **Figma blockers** | A Figma blocker is never raised from the main conversation's own tool access. The `ui-reviewer` runtime determines whether the Figma MCP is available |

## How it works

1. **Pin the inputs.** Check the Playwright CLI once per session with `playwright-cli --version`, falling back to `npx --no-install playwright cli --version` (never `npx playwright-cli`, a deprecated npm package). When neither responds, ask whether to install it now or wait. Then pin the Figma URL, the dev server URL, the component name and the task ID, and derive the shared verification root `specifications/<task-id>/ui-verification/` and the next `iteration-<N>/` directory.
2. **Delegate capture** to `ui-capture-worker` in one self-contained delegation and require its structured capture summary.
3. **Gate on artifacts.** Confirm all three ACTUAL files exist in the iteration directory and the shared `figma-expected.png` exists.
4. **Delegate judgment** to `ui-reviewer` with the Figma URL, the same pinned URL, the component name and the exact artifact directory. Save the report as `report.md` and relay the verdict, the complete difference table and the recommended fixes.
5. **On blockers,** resolve with the user: a missing or wrong URL, unexpected page content, a missing Figma reference, or a login redirect. Blockers consume no iteration budget.

## Reference Loading

| Reference | Load when |
| :-- | :-- |
| [`verifying-ui`](/docs/plugins/tsh-product-engineering/skills/verifying-ui), read as a file because it is not model-invocable and `ui-reviewer` preloads it | Interpreting a verdict, tolerances or the artifact contract |
| [`capturing-ui-evidence`](/docs/plugins/tsh-product-engineering/skills/capturing-ui-evidence) | A capture blocker needs diagnosing, or auth inputs must be prepared |
| The UI verification gate reference in `orchestrating-feature-implementation` | This pass runs inside feature delivery and returned FAIL |

## Related skills

- [`orchestrating-feature-implementation`](/docs/plugins/tsh-product-engineering/skills/orchestrating-feature-implementation): the full verify-fix loop, the 5-iteration budget and the escalation gate.
- [`verifying-ui`](/docs/plugins/tsh-product-engineering/skills/verifying-ui): the judging standard the reviewer applies.
- [`capturing-ui-evidence`](/docs/plugins/tsh-product-engineering/skills/capturing-ui-evidence): the capture contract.

For the end-to-end picture see the [UI verification workflow](/docs/workflows/ui-verification).

## Source

[`plugins/tsh-product-engineering/skills/reviewing-ui/SKILL.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-product-engineering/skills/reviewing-ui/SKILL.md)
