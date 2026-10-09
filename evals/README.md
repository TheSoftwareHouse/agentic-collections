# Checking skill routing

Two checks catch a skill that fires on the wrong request: a free description lint
that flags skills whose descriptions read alike, and a routing eval suite that
proves which skill Claude actually loads. A third, free check keeps the eval cases
honest. All three run from the repository root.

| Check | Command | Cost | Runs in CI |
| :-- | :-- | :-- | :-- |
| Description lint | `python3 scripts/lint-descriptions.py` | free, under a second | every pull request |
| Routing evals | the `claude plugin eval` command [below](#run-the-suite) | about USD 0.12 per case, billed to your account | pull requests touching `plugins/` or `evals/` |
| Case check | `python3 scripts/check-eval-cases.py` | free, under a second | every pull request |

Run the lint whenever you change a skill or agent description. Run the evals when
the lint flags your skill, or when you add or rename a model-invocable skill. Run
the case check whenever you add, change or rename a case or a skill.

## Description lint

The lint compares the routing text of every skill and agent the model can choose
on its own — the frontmatter `description` plus `when_to_use` — and ranks every
pair by word overlap. Overlap on rare words such as `figma` or `wcag` counts more
than overlap on common ones. A score of 0 means no shared vocabulary; 1 means
identical text. It compares words, not meaning, so a paraphrase can slip past it.

It leaves out what the model never chooses between:

- skills with `disable-model-invocation: true`, whose description is never loaded
- a skill and an agent from the same plugin, because the agent usually runs that
  skill and is picked at delegation time

### Read the result

| Level | Score | What happens |
| :-- | :-- | :-- |
| `ok` | 0.35 or below | nothing |
| `WARN` | above 0.35 | listed, and annotated on the pull request; the run still passes |
| `FAIL` | above 0.50 | exit 1; the pull request goes red |
| `allowed` | above 0.35, pair listed in `allowed_pairs` | listed, never fails; above 0.50 it shows as `WARN` |

Pairs from plugins that are never installed in the same repository get both
thresholds raised by 0.15 and are marked `[exclusive]`: the cloud providers
`tsh-stack-aws`, `tsh-stack-gcp` and `tsh-stack-azure`, and the backend runtimes
`tsh-stack-nodejs`, `tsh-stack-serverless` and `tsh-stack-python`.
`tsh-stack-frontend` is not in that group, because most projects pair a frontend
with a backend.

The run also exits 1 when a component's frontmatter cannot be parsed — a skipped
file would be a missed collision — or when `allowed_pairs` names a component that
no longer exists.

### Act on a flagged pair

1. Add the distinction to one or both descriptions, in the form this repository
   already uses: "Building accessible components is tsh-stack-frontend's
   ensuring-accessibility."
2. Write a routing case for the pair and run it with `--runs 6`
   ([measure one case](#measure-one-case)). The lint shows where to look; the eval
   shows whether routing is actually broken.
3. If the two genuinely route apart and the wording cannot diverge further, add
   the pair to `allowed_pairs` in `scripts/description-lint.json`, as the a11y
   pair already is:

   ```json
   { "a": "tsh-product-testing:auditing-accessibility",
     "b": "tsh-stack-frontend:ensuring-accessibility",
     "reason": "Audit vs build; a11y-audit-not-build and a11y-build-not-audit prove it." }
   ```

   IDs are `tsh-<plugin>:<skill>` for a skill and `tsh-<plugin>:@<agent>` for an
   agent, in either order.

### Options

| Option | Effect |
| :-- | :-- |
| `--top N` | rows to print; default 10. Use `--top 100` to see every pair near a threshold |
| `--warn-above F`, `--fail-above F` | override the thresholds from `scripts/description-lint.json` for one run |
| `--config PATH` | read thresholds, groups and allowed pairs from another file |
| `--github` | also emit GitHub annotations on the description line of both files, and append the full table to the job summary |

## Routing evals

Each case starts a real Claude session in a sandbox with the plugins it names,
sends one realistic request, stops after the first turn, and checks which skill
Claude loaded. One turn is enough because only the first Skill call is a routing
decision; on later turns a skill legitimately loads its companion skills.

A case is `evals/routing/<case>/case.yaml`. Its graders are plain text matches on
the Skill call — one asserts the right skill fired, one that its nearest sibling
did not — so grading itself costs nothing. You pay for the session.

### Run the suite

```shell
claude plugin eval . --eval-dir evals --tag routing \
  --trust-plugin --no-publish --ablation none \
  --model claude-sonnet-5-5 --threshold 1 --max-cost-usd 3 \
  --json evals/results/latest.json
```

| Flag | Why it is there |
| :-- | :-- |
| `.` with `--eval-dir evals` | Cases live at the repository root, not inside a plugin, because a collision needs two plugins in one session. Each case names the plugins it loads. |
| `--tag routing` | Selects the routing cases and skips quarantined ones tagged `known-failure`. |
| `--trust-plugin` | Answers the first-run trust prompt, which would otherwise block a non-interactive run. |
| `--no-publish` | Keeps the report local. **Without it the HTML report is published to claude.ai** whenever your account supports publishing. |
| `--ablation none` | Skips the second run without plugins. Routing has no meaningful baseline, and this halves the cost. |
| `--model claude-sonnet-5-5` | Pins the model, so a model rollout does not look like a skill regression. |
| `--threshold 1` | Every case must score 1, or the command exits 1. |
| `--max-cost-usd 3` | Stops the run, exit 2, once spend reaches the cap. |
| `--json PATH` | Writes the full result as JSON. |

Each case sets `runs: 1` and `max_turns: 1` itself; you do not pass them.

### Run one case

```shell
claude plugin eval . --eval-dir evals --case a11y-audit-not-build \
  --trust-plugin --no-publish --ablation none --model claude-sonnet-5-5
```

`--case` takes the case directory name, or a glob such as `'a11y-*'`.

### Measure one case

One run tells you whether a case can pass; six tell you how often it does. Use
this before quarantining a case and before lifting a quarantine:

```shell
claude plugin eval . --eval-dir evals --case ui-review-not-standard \
  --runs 6 -j 3 --trust-plugin --no-publish --ablation none \
  --model claude-sonnet-5-5 --max-cost-usd 2
```

`--runs 6` overrides the case's own `runs: 1`; `-j 3` runs three sessions at once.

### Read the result

The command prints one line per case and the path of an HTML report. Every run
writes `evals/results/<timestamp>/report.html` and `aggregate-result.json`; the
`--json` file is a copy of the latter.

| Exit code | Meaning |
| :-- | :-- |
| 0 | every case passed |
| 1 | a case failed, a case file did not load, or no case matched the filter |
| 2 | the `--max-cost-usd` cap or a rejected credential stopped the run early; results are partial |

A case passed when `passed` is `true` and `score` is 1. When it failed, each
grader's explanation says what happened — `Skill called 1x (expected 0..0)` means
the sibling skill fired.

These lines appear on **every** run, passing ones included, and are not failures:

| Line | Meaning |
| :-- | :-- |
| `exit 1: Reached maximum number of turns (1)` | The session was stopped after the routing decision, by design. The report shows it in the error field next to `passed: true`. |
| `[claude-code:unrecognized_model] {"model":"claude-sonnet-5-5",…}` | The CLI's price table lacks this model. The model runs normally. |
| `mocks: "plugin:tsh-product-testing:playwright", … NOT started` | Routing cases need no MCP server, so none is started. |

`evals/results/` is gitignored. Delete it whenever you like.

## Case check

A must-not-fire grader passes whenever its pattern matches nothing, so a
misspelled or renamed skill would leave it green forever, proving nothing. The
case check reads every `evals/routing/*/case.yaml` without running a model and
exits 1 when:

- a grader names a skill that none of the case's `plugins` ships, or one with
  `disable-model-invocation: true`
- `name` differs from the directory, or a plugin path does not resolve
- the case leaves the routing shape: `runs: 1`, `max_turns: 1`,
  `allowed_tools: [Skill]`, no `scaffold_script`, graders that are `tool_used` on
  `Skill` or a `regex` over the trace naming a skill or agent, and at least one
  must-not-fire grader
- the tags hold neither or both of `routing` and `known-failure`
- a `known-failure` case is missing from [Known failures](#known-failures), or
  that table lists a case that is not quarantined

- a model-invocable skill has no must-fire grader in a non-quarantined case and
  is not listed in `scripts/eval-coverage-baseline.json`
- that baseline lists a skill that now has such a case, or that no longer exists

The baseline holds the skills that predate the rule and have no case yet. It only
shrinks: a new skill fails the check until it has a case, and a skill that gains
one must leave the baseline in the same pull request. A quarantined case does not
count, so a skill whose only case is quarantined stays in the baseline.

The run prints how many model-invocable skills have a must-fire case.
`--coverage` lists the ones that have none; `--github` emits annotations on the
offending line.

The two scripts have unit tests in `scripts/tests/`:

```shell
python3 -m unittest discover -s scripts/tests
```

## In CI

| Workflow | Trigger | Does |
| :-- | :-- | :-- |
| `.github/workflows/quality.yml` | every pull request, and pushes to `main` | runs the script unit tests, the lint and the case check with `--github`, and `claude plugin validate` on the catalog and each plugin |
| `.github/workflows/plugin-evals.yml` | pull requests touching `plugins/**`, `evals/**` or the workflow itself | runs the suite command above; uploads `evals/results/` as the `routing-eval-results` artifact |

The eval workflow needs the `ANTHROPIC_API_KEY` repository secret. Without it — on
a fork, or before the secret is configured — the job prints a notice and passes
without running. Both workflows pin Claude Code 2.1.280; raise the pin only after
running the suite locally on the new version.

## Add or change a case

Copy an existing case directory and change the name, prompt, plugins and skill
names, then run the case check. Every new or renamed model-invocable skill needs
one must-fire and one must-not-fire case against its nearest sibling in the lint
ranking. The lint compares words, so also look for siblings it cannot see: a
discipline skill and a stack skill that cover the same job in different words,
such as `optimizing-cloud-cost` and `auditing-aws-cost`, are installed together in
most repositories.

When a request should load a discipline skill **and** a stack skill together —
the layering this repository is designed around — give the case two must-fire
graders, one per layer, plus a must-not-fire grader on a nearby skill that
belongs to neither, and tag it `layered`. `terraform-module-layers` is the worked
example. The case
shape, grader idioms and cost rules are in `.claude/rules/plugin-evals.md`, which
Claude Code loads when you open any file under `evals/`.

## Known failures

A case that exposes a real routing bug, whose fix belongs in a plugin change, is
quarantined: its tag changes from `routing` to `known-failure`, a comment above
the tag says why, and it is listed below. CI runs `--tag routing` only, so it
stays green while the case keeps documenting the bug. Never delete a quarantined
case or reword its prompt until it passes.

To lift a quarantine, fix the plugin, [measure the case](#measure-one-case) until
it passes 6 of 6, then restore the `routing` tag and remove its row here.

| Case | Observed | Fix lives in |
| :-- | :-- | :-- |
| `claude-extension-not-context` | A request to run prettier automatically after every edit loads Claude Code's built-in `update-config` instead of `authoring-claude-extensions` in 15 of 15 runs | `tsh-core`: decide whether `authoring-claude-extensions` claims hook requests, then reword its description or the case's expectation |
| `debug-not-implement` | A regression report loads `debugging-code` first in 5 of 6 runs; in the sixth Claude searches the code before any skill. As a ticket 1 of 6, with a stack trace naming files 0 of 6 | `tsh-product-engineering`: the `debugging-code` description, so it loads before code is read or searched |
| `nestjs-review-layers` | A pre-merge review of a pasted NestJS diff loads neither `reviewing-code` nor `implementing-nestjs-api` in 6 of 6 runs; Claude reviews it directly | `tsh-product-engineering` and `tsh-stack-nodejs`: the `reviewing-code` and `implementing-nestjs-api` descriptions |
| `terraform-module-layers` | Writing a reusable AWS RDS module loads both layers in 5 of 6 runs; in the sixth only `implementing-aws-terraform` | `tsh-platform-engineering`: the `implementing-terraform-modules` description |
| `ui-review-not-standard` | A "does this page match the Figma design" request loads `verifying-ui` instead of `reviewing-ui` in 5 of 6 runs | `tsh-product-engineering`: the `reviewing-ui` and `verifying-ui` descriptions |
