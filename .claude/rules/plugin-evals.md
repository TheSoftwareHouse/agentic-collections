---
paths:
  - "evals/**"
  - "plugins/*/evals/**"
---

# Plugin evals

**Routing cases prove the right skill fires when plugins are installed together; they
use free, deterministic graders and run on every pull request that touches `plugins/**`
or `evals/**` once the `ANTHROPIC_API_KEY` repository secret exists.** A new or renamed
model-invocable skill adds routing cases; a description change re-runs the suite. How
to run both checks, read their output, and lift a quarantine: `evals/README.md`.

## Where cases live

- **Routing cases: `evals/routing/<case>/case.yaml`, at the repository root.** A routing
  collision exists only when two plugins share a session, and a plugin cannot own a case
  that loads another. Each case lists the plugins it loads under `plugins:`, as paths
  relative to the case directory (`../../../plugins/<name>`). This is not a cross-plugin
  file reference in the sense of hard rule 7: nothing inside a plugin points at another
  plugin, and `evals/` is repository tooling like `templates/`, never installed.
- **Behavioural suites: `plugins/<plugin>/evals/<case>/case.yaml`.** They load their own
  plugin only and test what the skill makes Claude do after it fires. None exist yet.

## Case shape

```yaml
schema_version: "1.1"
name: <case-name>            # equals the directory name
description: <the routing decision the case asserts>
tags: [routing, cross-plugin]
plugins: ["../../../plugins/<a>", "../../../plugins/<b>"]
runs: 1
execution:
  prompt: |
    <a realistic teammate request, not a keyword list>
  max_turns: 1
  allowed_tools: [Skill]
graders: [...]
```

- **Routing cases use `max_turns: 1`.** A skill legitimately loads its companion skills
  on later turns, so only the first Skill call is a routing decision. The run ends with a
  "reached maximum number of turns" note that does not fail the case.
- `runs: 1`: a flaky case shows up as a red PR, which is itself a finding about the
  description. Measure a suspect case with `--runs 6`.
- `allowed_tools: [Skill]` and nothing else; see "Security" below for what it does and
  does not withhold.
- Write the prompt the way a teammate would phrase it. A negative control must belong to
  a different skill (`a11y-neither-on-unrelated` is a Playwright request).
- **Don't make the first turn about finding files.** The sandbox has no repository, but
  Glob, Grep and Read still work. A prompt that names a plan file, a pull request, or asks
  for "the files each task touches", makes Claude search before it loads a skill, and the
  turn cap ends the run with no Skill call. `implement-not-plan` went from 1 in 6 to 6 in
  6 once its prompt stopped pointing at an existing plan.
- **Don't paste the whole answer's input either.** Given a short snippet to review,
  Claude answered directly without loading any skill in 6 of 6 runs
  (`nestjs-review-layers`). That is a finding about the descriptions, so the case is
  quarantined rather than reworded around it.
- **Claude Code's built-in skills are in the session too**: `update-config`,
  `code-review`, `verify`, `debug`, `simplify` and others. A plugin skill can lose to one;
  `claude-extension-not-context` loses to `update-config`. A failing must-fire grader with
  no sibling fired is the sign.
- **A grader sees subagent tool calls.** When Claude delegates to an agent that loads the
  skill itself, the Skill call still counts, but the turn cap does not bound the
  subagent. Avoid prompts whose natural answer is delegation; graders cannot accept "the
  skill or the agent that runs it".

## Graders

| Type | Asserts | Cost |
| :-- | :-- | :-- |
| `tool_used` | A tool was called, optionally matching `input_match`, within `min`/`max` | free |
| `tool_order` | Tools were called in a given order | free |
| `regex` | A pattern matches or is absent in the output | free |
| `file_exists` | A file Claude created during the run matches a glob | free |
| `llm`, `baseline` | A judge model scores the output | calls a judge model |

Routing cases use `tool_used` on `Skill`. Both idioms, verified in this repo:

```yaml
# must fire
- name: audit-fired
  type: tool_used
  tool: Skill
  input_match: '"skill"\s*:\s*"(?:[\w-]+:)?<skill-name>"'
  arm: with-only

# must not fire
- name: build-not-fired
  type: tool_used
  tool: Skill
  input_match: '"skill"\s*:\s*"(?:[\w-]+:)?<other-skill-name>"'
  min: 0
  max: 0
```

The optional `<plugin>:` prefix in the pattern matches both `skill` and `plugin:skill`
spellings.

When the right answer is either loading a skill or delegating to the agent that runs it,
`tool_used` cannot say so, because it checks one tool. Use a `regex` over the trace with
one alternative per route; `ui-capture-not-judging` is the worked example:

```yaml
# must fire: the skill, or the agent that runs it
- name: capture-fired
  type: regex
  target: trace
  pattern: '(?:\\?"skill\\?"\s*:\s*\\?"(?:[\w-]+:)?<skill-name>\\?")|(?:\\?"subagent_type\\?"\s*:\s*\\?"(?:[\w-]+:)?<agent-name>\\?")'
```

Anchor every alternative on `"skill"` or `"subagent_type"`: the session's init line
lists every skill and agent by name, so a bare name always matches. `\\?` accepts the
quote with or without the JSON escaping the docs describe. Add `match: not_contains` for
a must-not-fire. `scripts/check-eval-cases.py` reads skill and agent names out of both
idioms, so keep to them. `arm: with-only` marks the must-fire grader as a plugin-fired indicator when
someone runs with ablation; CI runs `--ablation none`.

## Cost

**Every grader in this repo today is deterministic and free; the only spend is the model
turns.**

- One routing case-run costs about USD 0.08 to 0.12 and 9 s on `claude-sonnet-5-5`
  (measured 2026-10-07 and 2026-10-09). CI is capped by `max_turns: 1`,
  `--max-cost-usd 3` and a 15-minute timeout.
- `max_turns` does not bound a subagent. A run in which Claude delegated to
  `ui-capture-worker` cost USD 1.01 (2026-10-09).
- `tool_used`, `tool_order`, `regex` and `file_exists` cost nothing. An `llm` or
  `baseline` grader calls a judge model on every run, so add one only with a stated
  reason in the case `description`: what a deterministic grader cannot see.
- `--runs`, `--ablation with-without` and more cases multiply the bill. Say so in the PR.

Expected stderr, not a failure: the Playwright and Context7 mocks were not started, and
`[claude-code:unrecognized_model]` for `claude-sonnet-5-5` (the CLI price table lacks it).

## Rules for contributors

- **A new or renamed model-invocable skill adds at least one must-fire and one
  must-not-fire routing case**, the latter against its nearest sibling from
  `python3 scripts/lint-descriptions.py`. `scripts/check-eval-cases.py` enforces the
  must-fire half: a skill without one fails unless `scripts/eval-coverage-baseline.json`
  lists it, and that baseline only shrinks.
- **A layered request asserts both layers.** When a discipline skill and a stack skill
  should load together, give the case a must-fire grader for each and tag it `layered`. Skills with `disable-model-invocation: true`
  need none: their description is never preloaded.
- **A description change re-runs the suite** and the lint before the PR.
- **`python3 scripts/check-eval-cases.py` passes before the PR.** It is the only thing
  that notices a must-not-fire grader naming a skill that does not exist, which would
  otherwise pass forever. A skill rename updates every case that names it.
- **Look past the lint for the nearest sibling.** The lint compares words; a discipline
  skill and a stack skill doing the same job in different vocabulary score low and still
  collide, because the two plugins are installed together. `cloud-cost-audit-not-framework`
  is the worked example.
- **A case that exposes a real routing bug whose fix belongs in a plugin change is
  quarantined:** re-tag `routing` to `known-failure`, add a comment saying why, and list
  it in the Known failures table of `evals/README.md`. Never delete the case or reword
  its prompt until it passes. When the plugin is fixed, restore the `routing` tag.
- **Never commit `results/`.** `evals/results/` and `plugins/*/evals/results/` are
  gitignored.

## Security

A pull request supplies its own `case.yaml`, and CI runs it as the CI identity.
`allowed_tools` is not what keeps it contained. On Claude Code 2.1.280 a session with
`allowed_tools: [Skill]` still offered Task, Glob, Grep, Read, Skill, TaskStop and
ToolSearch, and a subagent did use Glob and Read in the sandbox's empty working
directory. Bash, Write, Edit and WebFetch were absent. Claude still tried to call Bash,
and the CLI refused it: "No such tool available: Bash. Bash is disabled for this session,
in subagents as well as here." The CLI withholds those tools unless `--allow-tools` grants
them, and without a scaffold there is nothing to read but the case's own sandbox.
`scripts/check-eval-cases.py` still enforces `allowed_tools: [Skill]` and rejects
`scaffold_script`, so a case cannot ask for more.

**Behavioural suites that need Bash, Edit or Write through `--allow-tools` or
`--scaffold` must not run in the PR workflow.** Run them locally or in a separate,
trusted-only workflow. Do not add `--allow-tools`, `--scaffold`, `--allow-real-servers`
or `--mocks off` to the CI command.
