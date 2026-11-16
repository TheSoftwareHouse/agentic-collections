# The verification skill

Load this in Step 2. The skill you write answers one question for every later
session: *which checks does this change need, and how are they run here?* A session
that cannot answer it either runs everything every time or, more often, runs too
little and reports the change done.

## 1. Where the checks come from

Read in this order. An earlier source wins when two disagree, and the disagreement
goes in the report.

| Source | What it gives you |
| --- | --- |
| CI workflows (`.github/workflows/`, `.gitlab-ci.yml`, `bitbucket-pipelines.yml`, `azure-pipelines.yml`, `Jenkinsfile`) | The full gate: what must pass before merge, in order, with the runtime versions and services CI provides |
| Task runners (`package.json` scripts, `Makefile`, `justfile`, `Taskfile.yml`, `composer.json` scripts, `pyproject.toml`, `tox.ini`, `noxfile.py`) | The local commands, including an aggregate such as `verify` or `check` that mirrors CI |
| Git hooks (`.husky/`, `lefthook.yml`, `.pre-commit-config.yaml`) | The fast checks the team already runs on every commit |
| Test configuration (Jest, Vitest, Mocha, pytest, PHPUnit and similar) | How suites are split — unit, integration, e2e — and which need a database, a container or an emulator |
| `CLAUDE.md` or `AGENTS.md` (whichever holds the instructions), `CONTRIBUTING.md`, the README's development section | Stated prerequisites, "before opening a pull request" steps, and known traps |

The project's `CLAUDE.md` may already state some of this as facts. The skill holds the
*procedure*; it may cite `CLAUDE.md`, never contradict it.

## 2. The full gate

- The gate is the set of CI jobs that must pass before merge. Jobs that deploy,
  publish, apply infrastructure or release are not checks, are never part of the
  gate, and are never run here, even when the same workflow file holds both.
- When a local aggregate command runs what the gate runs, it is the gate. Confirm by
  reading both, not by trusting the script's name.
- When there is none, the gate is the CI steps as a list of local commands, in CI's
  order.
- Name what a local run cannot reproduce — CI-only secrets, a matrix of runtime
  versions, a deploy preview — so nobody mistakes a green local run for a green CI.
- A variant that skips something (an offline mode, a fast mode) is recorded with what
  it skips. A result from it is never reported as fully verified.

## 3. Checks by change

Map the kinds of change this repository actually has to the smallest set of checks
that proves each one. Derive the kinds from its structure, not from a generic list.
Typical rows:

| Change touches | Usually needs |
| --- | --- |
| Application logic | The closest specs, then typecheck and lint |
| Request schemas, validation, middleware | Adjacent handler and validation tests as well |
| Database schema or migrations | The migration run against the database the project's own tooling starts locally (a compose service, an emulator), never one taken from `.env` alone, and the integration suites that read the changed tables |
| Infrastructure, IAM, configuration, dependencies, build | The full gate |
| Generated code (OpenAPI clients, ORM types) | Regenerate, inspect the diff, run the consumers' tests — never hand-edit the output. During capture, record this row without running the regeneration |
| Documentation only | Links, commands named in the text, formatting where tooling covers it |

Readiness for a pull request, or a request to verify everything, always means the full
gate.

## 4. Boundaries

Four boundaries go into every verification skill, because a verification that breaks
them does harm:

- Never run a check against production or a real third-party service.
- Never print a secret or an `.env` value; name the missing variable instead.
- Never change code, tests or thresholds to hide a failure the change did not cause;
  diagnose it and say which failures belong to the change.
- Report what was run, its result, and what was skipped and why. Never claim a check
  passed that was not run.

Add a project-specific boundary only with a source: a local emulator the suites need,
commands that collide (a build that overwrites what a running dev server serves), a
runtime version check, a suite that costs money or calls a paid sandbox, a server that
must not be started. Name the source next to it.

## 5. Proving the commands

Read before running. For each command, open the script or job it expands to and
follow it to the end: what it executes, which environment variables it reads and
where they resolve on this machine (`.env`, exported variables, CI secrets), and
whether anything it touches is shared, paid or external. A suite whose connection
string comes from `.env` may point at a shared database on a developer's clone; a
"test" script may call a paid sandbox. Such a command is written with what it needs
and marked not run, never executed to see what happens. An external system here is
one of the project's own: its providers, clouds, sandboxes and shared environments. A
read of a public package registry, such as a dependency audit, is not, and runs like
any other check.

A command that writes is not run during capture either, however local it is: a fixer
or format script, a snapshot update, a regenerate step, a migration, a seed or a
suite that resets tables. Run its read-only variant when the project has one
(`--check`, `--dry-run`, or a generator writing to a temporary directory, then
`git diff --no-index --exit-code <generated dir> <temp dir>`); otherwise record it
and mark it not run. Install dependencies
only when they are missing, and only with the lockfile frozen (`npm ci`,
`pnpm install --frozen-lockfile`, `composer install`, `uv sync --locked`).

Then run each remaining command, cheapest first. A required check that fails today,
such as a dependency audit with a real advisory or a lint with an existing
violation, stays in the skill like any other: leaving it out would make a shorter
list read as the full gate. Its failure goes in the report as the baseline status,
so the team knows the gate is red before any change. Do not start services
to make a command pass; write what it needs and mark it not run. Run a slow gate once,
and give its rough duration so later sessions can plan for it.

## 6. Template

Fill every `<…>`, delete rows that do not apply, and keep the result under ~100 lines.

```markdown
---
name: verifying-changes
description: "Selects and runs the checks a change to <project> needs — the closest tests, typecheck and lint for a small change, the full gate (`<command>`) before a pull request or for <infrastructure, dependency, configuration> changes — within the project's boundaries. Use to choose and run checks after implementing or fixing something. A failing check whose cause is unknown, a merge review and a security review belong to the team's debugging and review skills, which read this one."
---

# Verifying a change in <project>

Work from the repository root. Identify the files the current task changed; do not
assume every uncommitted file belongs to it.

## Checks by change

| Change touches | Run |
| --- | --- |
| `<glob>` | `<closest specs>`, then `<typecheck>` and `<lint>` |
| `<glob>` | the full gate |

## Full gate

`<command>` mirrors CI (`<workflow path>`). Run it for pull-request readiness, when
asked to verify everything, and for the rows marked above. Needs: <runtime version,
services>. <Variant and what it skips — its result is never "fully verified".>

## Boundaries

- Never run a check against production, a real third-party service or a shared
  environment; a database counts as local only when the project's own tooling
  starts it.
- <Project-specific boundary> (source: `<path>`).
- Never print a secret or an `.env` value; name the missing variable instead.
- Never change code, tests or thresholds to hide a failure the change did not cause.

## Report

The commands run and their results, the checks skipped and why, and the remaining
risk. Never claim a check passed that was not run.
```
