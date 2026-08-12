# agentic-collections

## What this repo is

A **Claude Code plugin marketplace** for The Software House. It is not an
application: there is no build step, no test suite, no dependencies, and no
runtime. Everything here is Markdown and JSON that Claude Code loads.

The repo publishes five plugins, one per discipline. Each plugin ships custom
**agents** and **skills** that TSH teams install into their own projects.

Install instructions for teammates live in [`README.md`](README.md) — that is the
canonical copy, don't duplicate the commands elsewhere.

## Layout

```text
.claude-plugin/marketplace.json   # the catalog — every plugin must be listed here
.claude/settings.json             # registers this marketplace for repo contributors
templates/                        # copy-paste sources; NOT loaded by Claude Code
├── agent.md
└── SKILL.md
plugins/
└── tsh-<discipline>/
    ├── .claude-plugin/
    │   └── plugin.json           # manifest — the ONLY file allowed in here
    ├── agents/                   # <agent-name>.md
    ├── skills/                   # <skill-name>/SKILL.md
    └── README.md
```

### Manifests

`<plugin-root>/.claude-plugin/plugin.json` is the **only** manifest path Claude Code
reads. A `plugin.json` placed at the plugin root is ignored — silently, with no load
error — so the nesting is not a stylistic choice. Only `plugin.json` may live in
`.claude-plugin/`; every component directory goes at the plugin root.

The manifest is technically optional: without one, Claude Code derives the plugin
name from the directory name and auto-discovers `agents/` and `skills/` at their
defaults, which is exactly this layout. We keep one per plugin anyway, because
`claude plugin validate ./plugins/<name>` fails outright without it
(`No manifest found in directory`), and because it keeps each plugin
self-describing if it is ever vendored elsewhere or split into its own repo.

## Plugin scopes

Route every contribution to the plugin that owns the work:

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

## Where things go

| I want to add… | Path | Start from |
| :-- | :-- | :-- |
| An agent | `plugins/<plugin>/agents/<agent-name>.md` | `templates/agent.md` |
| A skill | `plugins/<plugin>/skills/<skill-name>/SKILL.md` | `templates/SKILL.md` |
| Supporting detail for a skill | `plugins/<plugin>/skills/<skill-name>/reference.md` | — |
| A script a skill runs | `plugins/<plugin>/skills/<skill-name>/scripts/` | — |
| A whole new plugin | `plugins/tsh-<discipline>/` + an entry in `marketplace.json` | an existing plugin |

### Agent or skill?

- **Agent** — delegated work in its own context with its own system prompt and its
  own tool restrictions. Use it when the work is a self-contained job whose
  intermediate reasoning should stay out of the main conversation: audits,
  reviews, focused investigations. Invoked as `@tsh-product-testing:a11y-auditor`.
- **Skill** — instructions loaded into the *current* context. Use it when the work
  is a procedure the main agent should follow inline, with full access to what the
  conversation already knows. Invoked as `/tsh-product-testing:audit-page`.

Rule of thumb: if it needs to hand back a report, make it an agent. If it needs to
change the way the current conversation proceeds, make it a skill.

## Naming

- Plugin directories: `tsh-<discipline>`, kebab-case. The directory name, the
  `name` in `plugin.json`, and the `name` in the marketplace entry must all match.
- Agent and skill names: kebab-case, **without** a `tsh-` prefix. The plugin
  already namespaces them.
  - Correct: `a11y-auditor` → `@tsh-product-testing:a11y-auditor`
  - Wrong: `tsh-a11y-auditor` → `@tsh-product-testing:tsh-a11y-auditor`
- Agent filename matches its frontmatter `name`. Skill directory name *is* the
  skill name.

## Hard rules

1. **Only `plugin.json` goes inside `.claude-plugin/`.** `agents/`, `skills/`,
   `hooks/` and everything else live at the plugin root. Putting them under
   `.claude-plugin/` is the single most common plugin bug and fails silently.
2. **A new plugin must be added to `.claude-plugin/marketplace.json`** or nobody
   can install it. The marketplace file is the catalog; the plugin directory alone
   is invisible.
3. **Bump `version` in the plugin's `plugin.json` when shipping a change — that
   file only.** Claude Code resolves a plugin's version from `plugin.json` first,
   then the marketplace entry, then the commit SHA. Because `plugin.json` always
   wins, `marketplace.json` deliberately carries no `version` field; adding one
   back would shadow nothing and mislead the next contributor. Teammates receive
   an update only when this string changes — push without bumping it and
   `/plugin update` reports "already at the latest version", with no error to
   explain why nothing arrived.
4. **A `CLAUDE.md` inside a plugin is not loaded.** Claude Code ignores it. To ship
   instructions that reach Claude's context, write a skill. Per-plugin human docs
   go in that plugin's `README.md`.
5. **Plugin agents may not declare `hooks`, `mcpServers`, or `permissionMode`.**
   Claude Code rejects those fields in plugin-shipped agents for security reasons.
6. **Keep `templates/` out of the plugins.** It sits at the repo root precisely so
   Claude Code never loads the examples as real components.

## Local development loop

Load a plugin straight from the working tree — no install, no marketplace:

```shell
claude --plugin-dir ./plugins/tsh-product-testing
```

Then, while iterating:

```shell
/reload-plugins                                    # pick up file changes
/plugin list                                       # confirm it loaded
/context                                           # agents appear under Custom Agents
```

`/reload-plugins` counts only `commands/`, so a `0 skills` summary is normal here
and does not mean the skill failed to load.

Validate before pushing:

```shell
claude plugin validate ./plugins/tsh-product-testing   # per plugin
claude plugin validate .                               # the marketplace catalog
```

Expect `✔ Validation passed`. Warnings don't fail validation; add `--strict` to
treat them as errors.

To test the catalog end to end without pushing, add the repo as a local
marketplace, then remove it so it doesn't shadow the GitHub copy:

```shell
/plugin marketplace add ./
/plugin marketplace remove tsh-agentic-collections
```

## Reference

- Creating plugins: https://code.claude.com/docs/en/plugins
- Marketplaces: https://code.claude.com/docs/en/plugin-marketplaces
- Full schemas: https://code.claude.com/docs/en/plugins-reference
- Skills: https://code.claude.com/docs/en/skills
- Subagents: https://code.claude.com/docs/en/sub-agents
