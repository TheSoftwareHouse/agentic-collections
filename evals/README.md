# Evals

Routing evals prove that the right skill fires when several plugins are installed together. They run with `claude plugin eval`, use deterministic graders only, and are never installed. Policy and case shape: `.claude/rules/plugin-evals.md`.

- `evals/routing/<case>/case.yaml` — routing cases. They live at the repository root because a collision exists only when two plugins share a session; each case lists the plugins it loads under `plugins:`, as paths relative to the case directory.
- `plugins/<plugin>/evals/` — behavioural suites for one plugin, loading that plugin only. None exist yet.

## Running the routing suite

```shell
claude plugin eval . --eval-dir evals --tag routing \
  --trust-plugin --no-publish --ablation none \
  --model claude-sonnet-5-5 --threshold 1 --max-cost-usd 3 \
  --json evals/results/latest.json
```

Exit 0 means every case passed. Each case runs one turn, because only the first Skill call is a routing decision; the "reached maximum number of turns" note in the output is expected and does not fail a case. One case-run costs about USD 0.12 and 9 seconds on `claude-sonnet-5-5`, billed to the signed-in account. Two other stderr lines are expected too: the Playwright and Context7 mocks were not started, and `[claude-code:unrecognized_model]`, which only means the CLI's price table lacks that model.

`evals/results/` and `plugins/*/evals/results/` are gitignored; never commit run output.

## Known failures

A case that exposes a real routing bug, but whose fix belongs in a plugin change, is tagged `known-failure` instead of `routing`, with a comment saying why. CI runs `--tag routing` only, so it stays green while the case keeps documenting the bug. Run a quarantined case with `--tag known-failure --runs 6` to measure it. Fix the plugin, then swap the tag back.

| Case | Observed | Fix lives in |
| :-- | :-- | :-- |
| `ui-review-not-standard` | A "does this page match the Figma design" request loads `verifying-ui` instead of `reviewing-ui` in 5 of 6 runs | `tsh-product-engineering`: the `reviewing-ui` and `verifying-ui` descriptions |

