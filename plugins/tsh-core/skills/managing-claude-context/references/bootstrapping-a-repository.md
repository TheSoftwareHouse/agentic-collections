# Bootstrapping a repository

Use this reference when Step 1 found no existing context files. The goal of a first
pass is a small, entirely true `CLAUDE.md` — not a complete one. Completeness is
what produces the 400-line file nobody trusts.

## 1. Decide whether to start from `/init`

Claude Code ships `/init`, which analyses the codebase and generates a starting
`CLAUDE.md`. It is a reasonable first draft and it does one thing worth having:
it reads other tools' configuration and folds the relevant parts in — Cursor rules
from `.cursor/rules/` or `.cursorrules`, and Copilot rules from
`.github/copilot-instructions.md`.

Setting `CLAUDE_CODE_NEW_INIT=1` enables an interactive flow that asks which
artifacts to set up, explores with a subagent, asks follow-up questions, and shows a
reviewable proposal before writing. It also reads `AGENTS.md`, `.devin/rules/`,
`.windsurf/rules/` and `.clinerules`.

Use `/init` when the repository has existing agent configuration to absorb. Skip it
when there is none and you already understand the project — a generated draft you
then have to cut down can cost more than writing 60 good lines.

Either way the output is a **draft**. Every command in it still has to be run, and
every claim still has to be checked, before it is committed.

## 2. Migrating from GitHub Copilot

The mapping is close to one-to-one:

| Copilot | Claude Code |
| --- | --- |
| `.github/copilot-instructions.md` | root `CLAUDE.md` |
| `.github/instructions/*.instructions.md` with `applyTo:` | `.claude/rules/*.md` with `paths:` |
| `applyTo: 'src/**/*.ts'` | `paths: ["src/**/*.ts"]` |
| `.github/skills/<name>/SKILL.md` | `.claude/skills/<name>/SKILL.md` |
| `.github/prompts/*.prompt.md` | a skill — Claude Code has no separate prompt layer |

Two differences that matter when porting:

- `applyTo` takes a single glob string; `paths` takes a YAML list, so several
  Copilot instruction files that differ only by glob often collapse into one rule.
- Copilot may apply an instruction file by semantic match on its `description` even
  without an `applyTo` match. Claude Code's `paths` does not work that way — it
  matches globs only. An instruction that relied on description matching needs to
  become a skill, where description routing is the mechanism.

`/import` (Claude Code v2.1.213 or later) brings a supported agent's configuration
across in one step, appending instruction files such as `AGENTS.md` to the matching
`CLAUDE.md` and carrying over MCP servers, commands, subagents and skills. It is a
one-time copy, not a live link, so the copies diverge from that point on.

**Do not port an instruction you have not verified.** Instruction files rot quietly,
and a migration is where the rot becomes permanent. Check each claim against the
current code before it lands in `CLAUDE.md`.

## 3. Inspection order

Read in this order, because each step tells you what the next one should confirm:

1. **`README.md` and `CONTRIBUTING.md`** — the conventions the team already wrote
   down. Do not restate them; note which are still true.
2. **The manifest** — `package.json`, `go.mod`, `pyproject.toml`, `composer.json`.
   Take the *scripts*, not the dependency list.
3. **CI configuration** — the most reliable source of the commands that actually
   have to pass. When CI and the README disagree, CI is right.
4. **Linter, formatter and type-checker configuration** — everything enforced here
   is something you must **not** write into `CLAUDE.md`.
5. **Test setup** — how tests are located, named and run; what a test needs to have
   running before it passes.
6. **A representative slice of source** — two or three files in different areas,
   enough to see the conventions the tooling does not enforce.
7. **Existing `docs/decisions/`, `docs/adr/` or equivalent** — see
   [`indexing-decision-records.md`](./indexing-decision-records.md).

## 4. Run the commands

Every command that goes into `CLAUDE.md` gets executed first. This is the single
highest-value step in a bootstrap and the one most often skipped.

Commands taken from a README are guesses until proven: they go stale, they assume a
package manager that changed, they omit a required environment variable, they need a
service that has to be running. A `CLAUDE.md` whose build command fails teaches the
model that the file is unreliable, and it will weight the rest of it accordingly.

When a command cannot be run in the current environment, say so in the file rather
than asserting it works — "`npm run e2e` requires a local Postgres on 5432" is
useful; an unqualified `npm run e2e` that fails is not.

## 5. Ask rather than infer

A convention seen in one file is a coincidence. A convention seen in three files is
a pattern. A convention seen in three files that contradict each other is a question
for the team.

Ask when:

- Two areas of the codebase disagree and neither is obviously legacy
- A pattern looks deliberate but its rationale is not recoverable from the code
- The repository is mid-migration and both the old and new shapes are present

Never resolve these by picking the one you prefer. Write down what is settled, list
what is not, and let the team decide. An invented convention written confidently is
the worst possible outcome of this procedure — it is indistinguishable from a real
one and it propagates.

## 6. First pass, in order

1. Root `CLAUDE.md`: what the repo is, the verified commands, the pitfalls, and
   pointers to the other layers. Under 200 lines, ideally far under.
2. One or two path-scoped rules for the conventions that clearly follow file types.
   Do not build the whole rule set up front — add rules when a convention is
   actually violated, so each one has evidence behind it.
3. A nested `CLAUDE.md` per package **only** if the repository is already a monorepo
   with distinct owners. See [`monorepos-and-scale.md`](./monorepos-and-scale.md).
4. `docs/decisions/README.md` if decision records exist or the team wants them.
5. Verify with `/context`, then hand the result to a human who knows the project.
   A first pass is a proposal, not a finished artifact.
