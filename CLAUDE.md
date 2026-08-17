# agentic-collections

## What this repo is

A **Claude Code plugin marketplace** for The Software House. It is not an
application: there is no build step, no test suite, no dependencies, and no runtime.
Everything here is Markdown and JSON that Claude Code loads.

It publishes three families: `tsh-<discipline>` for *how we work*,
`tsh-stack-<stack-name>` for *what we work with*, and `tsh-core` — a single,
deliberately small plugin for tool mechanics that depend on neither.

Install instructions for teammates live in `README.md` — that is the canonical copy,
don't duplicate the commands elsewhere.

## Plugin scopes

Route every contribution to the plugin that owns the work.

### Disciplines — *how we work*

| Plugin | Owns |
| :-- | :-- |
| `tsh-product-engineering` | Feature implementation, code review, refactoring, debugging, TDD workflows |
| `tsh-product-testing` | E2E testing, accessibility testing, exploratory/manual QA, test-plan authoring |
| `tsh-product-management` | Business analysis, requirements & user stories, discovery and scoping |
| `tsh-product-design` | UI/UX design work, design systems, design review, Figma-driven flows |
| `tsh-platform-engineering` | Infrastructure, CI/CD, IaC, containers, observability, deployment |

If a contribution genuinely spans two disciplines, put it in the one that owns the
*outcome*, not the one that owns the tooling. An a11y audit belongs to
`tsh-product-testing` even though it reads component code.

### Stacks — *what we work with*

| Plugin | Owns |
| :-- | :-- |
| `tsh-stack-frontend` | Browser-targeted code — TypeScript configuration for bundler-resolved apps, currently React and Vite |
| `tsh-stack-nodejs` | Server-side JavaScript runtimes — TypeScript configuration for Node, and the frameworks TSH builds on it, currently NestJS |

Every technology stack gets its own plugin, created when it has real content to ship,
not before. Read `.claude/rules/stack-plugin-conventions.md` before adding a stack
plugin or moving guidance between two of them.

### Core — *neither role nor stack*

| Plugin | Owns |
| :-- | :-- |
| `tsh-core` | What holds regardless of discipline and stack — Git worktree lifecycle, the house standard for writing technical documents, the project-context files Claude Code loads, and the decision-record format and lifecycle |

**Read `.claude/rules/core-plugin-admission.md` before adding anything to
`tsh-core`.** It carries the highest admission bar in the repo, because everyone who
installs it pays listing budget for every entry.

### Which family?

Ask in order and stop at the first yes:

1. *Would this guidance change if the repo switched language or framework?*
   → `tsh-stack-<stack-name>`. "What to look for in a NestJS pull request."
2. *Would it change if the reader switched job?* → the `tsh-<discipline>` that owns
   the **outcome**. "How we run code review."
3. *Neither, and it clears the admission bar?* → `tsh-core`. "How to create a Git
   worktree without losing work."

**Ties go to a discipline plugin. `tsh-core` is never the default answer.**

The split exists so the families can install differently: a discipline plugin travels
with **you** at `user` scope, a stack plugin with the **repo** at `project` scope,
and `tsh-core` with you, because it depends on nothing at all.

## Where things go

| I want to add… | Path | Start from |
| :-- | :-- | :-- |
| An agent | `plugins/<plugin>/agents/<agent-name>.md` | `templates/agent.md` |
| A skill | `plugins/<plugin>/skills/<skill-name>/SKILL.md` | `templates/SKILL.md` |
| Supporting detail for a skill | `plugins/<plugin>/skills/<skill-name>/references/<topic>.md` | — |
| A script a skill runs | `plugins/<plugin>/skills/<skill-name>/scripts/` | — |
| A whole new plugin | `plugins/tsh-<discipline>/` or `plugins/tsh-stack-<stack-name>/` + an entry in `.claude-plugin/marketplace.json` | an existing plugin |
| A skill that fits no discipline and no stack | `plugins/tsh-core/skills/<skill-name>/SKILL.md` — read `.claude/rules/core-plugin-admission.md` first | `templates/SKILL.md` |
| To ship any of the above to teammates | invoke `/releasing-a-plugin-change` | — |

**Before creating any of them, invoke `/contributing-a-plugin-component`** — it routes
placement, naming and the `tsh-core` admission test, then hands the authoring
mechanics to `/tsh-core:authoring-claude-extensions`. The `.claude/rules/` files below
fire only when Claude *reads* a matching file, so they cannot reach you while you are
writing a new one.

`spec/` holds implementation specifications and is gitignored.

## Naming

- Plugin directories: `tsh-<discipline>`, `tsh-stack-<stack-name>`, or the fixed
  single name `tsh-core`, kebab-case. The directory name, the `name` in
  `plugin.json`, and the `name` in the marketplace entry must all match.
- **`tsh-core` is a single plugin — there is no `tsh-core-*`.** Both neighbouring
  families are prefixed, so this is the obvious thing to get wrong. Don't rename it
  to `tsh-common` or `tsh-shared` either — the name is load-bearing.
- Agent and skill names: kebab-case, **without** a `tsh-` prefix. The plugin already
  namespaces them. Correct: `a11y-auditor` → `@tsh-product-testing:a11y-auditor`.
- Agent filename matches its frontmatter `name`. Skill directory name *is* the skill
  name.
- **Skill names carry no framework version and stay tech-qualified.**
  `implementing-nestjs-api`, never `implementing-nestjs-11-api` or `implementing-api`.
  The name is the invocation command, so a pinned major forces a rename on every
  upgrade; and the model routes on descriptions, where two near-identical ones are a
  coin flip.

Rationale lives in `.claude/rules/authoring-skills.md` and
`.claude/rules/authoring-agents.md`.

## Hard rules

1. **Only `plugin.json` goes inside `.claude-plugin/`.** `agents/`, `skills/`,
   `hooks/` and everything else live at the plugin root. This is the single most
   common plugin bug and it fails silently. See
   `.claude/rules/plugin-manifests-and-marketplace.md`.
2. **A new plugin must be added to `.claude-plugin/marketplace.json`** or nobody can
   install it — and teammates only see it after
   `/plugin marketplace update tsh-agentic-collections`, which the announcement must
   name. See `.claude/rules/plugin-manifests-and-marketplace.md`.
3. **Bump `version` in the plugin's `plugin.json` and add a `CHANGELOG.md` entry in
   the same commit as the change — that file only, never `marketplace.json`.** Before
   committing any change under `plugins/`, invoke `/releasing-a-plugin-change`; it
   carries the bump level, the changelog format, and the announcement command. Push
   without the bump and `/plugin update` reports "already at the latest version",
   with no error to explain why nothing arrived.
4. **A `CLAUDE.md` inside a plugin is not loaded.** Claude Code ignores it. To ship
   instructions that reach Claude's context, write a skill. Per-plugin human docs go
   in that plugin's `README.md`.
5. **Plugin agents may not declare `hooks`, `mcpServers`, or `permissionMode`.**
   Claude Code rejects those fields in plugin-shipped agents for security reasons.
   See `.claude/rules/authoring-agents.md`.
6. **Keep `templates/` out of the plugins.** It sits at the repo root precisely so
   Claude Code never loads the examples as real components.
7. **Cross-link only inside your own plugin** — `./references/<topic>.md`, or
   `${CLAUDE_PLUGIN_ROOT}/…` between skills of the same plugin. Never path into
   another plugin: it may not be installed, and the failure is a silent dead link
   rather than an error. See `.claude/rules/authoring-skills.md`.
8. **Progressive disclosure above ~150 lines.** `SKILL.md` keeps the frontmatter,
   applicability, the non-negotiable rules table, a **Reference Loading** table with a
   "Load when" column, and the procedure; detail goes to `references/`, ≤300 lines
   each. A rule that blocks review stays in `SKILL.md` regardless. See
   `.claude/rules/authoring-skills.md`.
9. **`tsh-core` admits by elimination and evidence, and every addition discloses its
   cost.** It lands there only if it fails both routing questions, wraps a named tool
   rather than a TSH opinion, and the PR names which three of the five disciplines
   would invoke it in a normal month plus the plugin's routing footprint before and
   after. Ties go to a discipline plugin. This is a hard rule because a wrongly-placed
   skill loads fine, validates fine, and simply taxes everyone's context forever. See
   `.claude/rules/core-plugin-admission.md`.

## Local development loop

Load a plugin straight from the working tree — no install, no marketplace — then
iterate:

```shell
claude --plugin-dir ./plugins/tsh-core              # launch, then inside the session:
/reload-plugins                                    # pick up file changes
/plugin list                                       # confirm it loaded
/context                                           # agents appear under Custom Agents
```

`/reload-plugins` counts only `commands/`, so a `0 skills` summary is normal here and
does not mean the skill failed to load.

Validate before pushing:

```shell
claude plugin validate ./plugins/tsh-core   # per plugin
claude plugin validate .                    # the marketplace catalog
```

Expect `✔ Validation passed`. Warnings don't fail validation; add `--strict` to treat
them as errors. To test the catalog end to end without pushing, see
`.claude/rules/plugin-manifests-and-marketplace.md`.

## Where the rest lives

Authoring rationale is in `.claude/rules/`, one file per concern, loaded only when you
read a file it governs — the pointers above say which and when. Anything needed
*before* a file exists is a skill instead: `/contributing-a-plugin-component` to place
and name a component, `/releasing-a-plugin-change` to ship it.

## Reference

- Creating plugins: https://code.claude.com/docs/en/plugins
- Marketplaces: https://code.claude.com/docs/en/plugin-marketplaces
- Full schemas: https://code.claude.com/docs/en/plugins-reference
- Skills: https://code.claude.com/docs/en/skills
- Subagents: https://code.claude.com/docs/en/sub-agents
