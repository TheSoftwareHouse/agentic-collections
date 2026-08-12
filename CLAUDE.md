# agentic-collections

## What this repo is

A **Claude Code plugin marketplace** for The Software House. It is not an
application: there is no build step, no test suite, no dependencies, and no
runtime. Everything here is Markdown and JSON that Claude Code loads.

The repo publishes three families of plugins. **Discipline** plugins (`tsh-<discipline>`)
cover *how we work* — one per discipline, installed by the people who do that job.
**Stack** plugins (`tsh-stack-<stack-name>`) cover *what we work with* — one per
technology stack, installed into the projects built on it. **`tsh-core`** is the
ground under both: a single, deliberately small plugin for tool mechanics that
depend on neither your role nor the repo's technology. Each plugin ships custom
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
├── tsh-core/                     # neither role nor stack — one plugin, capped at 6 skills
│   └── …                         # identical shape
├── tsh-<discipline>/             # how we work — one per discipline
│   ├── .claude-plugin/
│   │   └── plugin.json           # manifest — the ONLY file allowed in here
│   ├── agents/                   # <agent-name>.md
│   ├── skills/                   # <skill-name>/SKILL.md + references/<topic>.md
│   └── README.md
└── tsh-stack-<stack-name>/       # what we work with — one per technology stack
    └── …                         # identical shape
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

**Every technology stack gets its own plugin, named `tsh-stack-<stack-name>`.**
PHP, Java, Go and the rest are expected members of this family; each is created
when it has real content to ship, not before. An empty plugin in the Discover tab
teaches teammates the catalogue is hollow.

### Core — *neither role nor stack*

| Plugin | Owns |
| :-- | :-- |
| `tsh-core` | What holds regardless of discipline and stack — Git worktree lifecycle, and the house standard for writing technical documents |

**`tsh-core` is one plugin, not a family. There is no `tsh-core-*`.** See
[Core plugin admission](#core-plugin-admission) before adding anything to it.

> **Which family?** Ask in order and stop at the first yes:
>
> 1. *Would this guidance change if the repo switched language or framework?*
>    → `tsh-stack-<stack-name>`. "What to look for in a NestJS pull request."
> 2. *Would it change if the reader switched job?* → the `tsh-<discipline>` that
>    owns the **outcome**. "How we run code review."
> 3. *Neither, and it clears the admission bar?* → `tsh-core`. "How to create a
>    Git worktree without losing work."
>
> **Ties go to a discipline plugin. `tsh-core` is never the default answer.**

The families are installed differently, and the split exists to make that
possible. A discipline plugin travels with **you** (`user` scope — your job
doesn't change per repo). A stack plugin travels with the **repo** (`project`
scope — the repo already knows what it's written in). `tsh-core` travels with
you too, at `user` scope, because it depends on nothing at all.

The underlying constraint is context budget. Collapsing stacks into
`tsh-product-engineering` would put every stack's skills in front of every
engineer: Claude Code preloads every installed skill's `name` and `description`
into context, and when that listing overflows its budget it *truncates
descriptions*, degrading routing for every skill including the discipline ones.
That argument is about **relevance density**, which is why it does not also
forbid a small universal plugin — a skill relevant to every installer costs
exactly one description, the floor for shipping it at all. But it does mean
`tsh-core` carries the highest admission bar in the repo, because everyone pays
for every entry in it.

### Stack plugin granularity

**A stack is a runtime target, not a language.** `tsh-stack-frontend` and
`tsh-stack-nodejs` both carry TypeScript guidance, and that is the design rather
than a duplication to clean up. Three reasons:

1. **Most projects have a frontend, whatever the backend is.** A Go or PHP team
   writing React must be able to install the frontend guidance without dragging a
   NestJS surface into their skill listing. A language-shaped plugin makes that
   impossible.
2. **The configuration genuinely diverges.** A bundler-resolved browser app
   (`moduleResolution: bundler`, `jsx`, `lib: DOM`, emit owned by Vite) and a Node
   service (`module: nodenext`, `emitDecoratorMetadata`, `outDir`) do not share one
   baseline `tsconfig.json`. There is no language-level core big enough to be worth
   a plugin of its own.
3. **A plugin is one install decision.** The install unit is the plugin, not the
   skill; there is no way to install half of one. Nobody wants "Node guidance but
   explicitly not the TypeScript settings it depends on."

Framework skills still live inside their runtime's plugin: `implementing-nestjs-api`
belongs in `tsh-stack-nodejs`, not in a `tsh-stack-nestjs` of its own. What changed
is where the boundary falls, not that frameworks get their own plugins.

**Split trigger.** When a `tsh-stack-*` plugin exceeds roughly 8 skills, or when
more than half its skills are irrelevant to a typical installer, split it — again
along a target boundary people actually install separately. For `tsh-stack-nodejs`
that would mean a serverless or CLI plugin peeling off if that guidance grows and
stops being relevant to service authors; it does **not** mean one plugin per
framework.

### Deliberate duplication across stack plugins

Two stack plugins needing the same knowledge is expected, and hard rule 7 makes
linking between them impossible. So the knowledge is **duplicated**, on purpose:
`configuring-typescript-for-frontend` and `configuring-typescript-for-nodejs` both
carry version policy, a strictness ladder, and an upgrade procedure.

Three rules keep that from rotting:

1. **Name the copies differently, and write genuinely different descriptions.** The
   model routes on descriptions; two near-identical ones are a coin flip. Naming the
   target in the skill name is what makes them distinguishable at all.
2. **Let the divergent parts diverge.** Copying a file and never adapting it is how
   the frontend skill ends up recommending `emitDecoratorMetadata`. If a section is
   identical in both copies *and* would stay identical under any future edit, that is
   a signal the content belongs to neither target specifically — reconsider whether
   it needs to ship at all.
3. **When you change one copy, check the other in the same PR.** Say in the commit
   message which copies you touched and which you deliberately left alone.

### Core plugin admission

Every other plugin has a claimant and an affirmative question — *is this QA's
job?*, *is this TypeScript?*. `tsh-core` is the only one defined by a
**negation**, and negatively-defined containers accrete by default. The cost is
also externalised: the contributor who couldn't decide gets a home for their
skill, while every teammate pays listing budget. So admission is by elimination
**plus evidence**:

1. **It fails both routing questions.** Not stack, not discipline.
2. **Generic is not core.** Core skills are *tool mechanics* — the procedure is
   dictated by the tool's own semantics (`git`, `gh`, the shell), not by TSH's
   opinion about how to work. "Write good commit messages" is generic, applies to
   everyone, and is still a **discipline** skill, because only TSH's opinion could
   produce it. **If you cannot name the tool the skill wraps, it is not core.**
   *One named exception exists:* `writing-technical-documents` is admitted as the
   house writing standard despite wrapping no tool, because every discipline's
   written deliverables are judged by it. It is the **only** exception, and it is
   named rather than generalised — there is no "output standards" category to file
   the next thing under. Commit-message and PR-title conventions are outside it and
   remain discipline skills.
3. **Evidence, not assertion.** The PR names which **three of the five
   disciplines** would invoke it in a normal month. "It's generic" is not evidence.
4. **Ties go to a discipline plugin.** When the answer is arguable, it isn't core.

**No cap — a disclosure instead.** There is no maximum number of skills here. There
is an obligation to state the cost at the moment someone chooses to pay it: a PR
adding a skill to `tsh-core` reports the plugin's **routing footprint** — the
combined `name`, `description` and `when_to_use` characters across its skills —
before and after. Claude Code preloads that text for every installed skill in order
to route on it; `description` and `when_to_use` are truncated together at 1,536
characters per skill, and when the whole listing overflows, descriptions are cut
and routing degrades for *every* skill in *every* plugin, not just the new one. A
count of skills never measured that — three terse skills can cost less than one
verbose one. Report the number, name the three disciplines, and let the reviewer
weigh it.

Growth is never a reason to split into `tsh-core-*`. A prefixed family earns its
keep only when there is a variable to instantiate (`tsh-stack-<stack-name>`,
`tsh-<discipline>`), and `tsh-core`'s defining property is depending on no
variable. The only thing that could follow `tsh-core-` is a topic bucket, and a
topic is not an install decision. When this plugin feels heavy, the fix is
re-homing what should never have been admitted.

The name is doing guardrail work, so don't "clarify" it later: `common` and
`shared` are the industry's canonical junk-drawer names because they claim *mere
reuse*, which anyone can truthfully assert about anything. `core` claims
*centrality*, which has to be defended.

Out of scope by construction: language or framework content (→ stack); role
practice and methodology (→ discipline); company policy, onboarding or handbook
prose (that's a document, not a skill); "utilities" and one-off automation; and
anything used by a single team or a single repo.

## Where things go

| I want to add… | Path | Start from |
| :-- | :-- | :-- |
| An agent | `plugins/<plugin>/agents/<agent-name>.md` | `templates/agent.md` |
| A skill | `plugins/<plugin>/skills/<skill-name>/SKILL.md` | `templates/SKILL.md` |
| Supporting detail for a skill | `plugins/<plugin>/skills/<skill-name>/references/<topic>.md` | — |
| A script a skill runs | `plugins/<plugin>/skills/<skill-name>/scripts/` | — |
| A whole new plugin | `plugins/tsh-<discipline>/` or `plugins/tsh-stack-<stack-name>/` + an entry in `marketplace.json` | an existing plugin |
| A skill that fits no discipline and no stack | `plugins/tsh-core/skills/<skill-name>/SKILL.md` — read [Core plugin admission](#core-plugin-admission) first | `templates/SKILL.md` |
| A note about what a released version changed | `plugins/<plugin>/CHANGELOG.md`, in the same commit as the `version` bump | `plugins/tsh-core/CHANGELOG.md` |

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

- Plugin directories: `tsh-<discipline>`, `tsh-stack-<stack-name>`, or the fixed
  single name `tsh-core`, kebab-case. The directory name, the `name` in
  `plugin.json`, and the `name` in the marketplace entry must all match.
- **`tsh-core` is a single plugin — there is no `tsh-core-*`.** The two
  neighbouring families are prefixed, so this is the obvious thing to pattern-match
  and get wrong. Don't rename it to `tsh-common` or `tsh-shared` either; see
  [Core plugin admission](#core-plugin-admission) for why the name is load-bearing.
- Agent and skill names: kebab-case, **without** a `tsh-` prefix. The plugin
  already namespaces them.
  - Correct: `a11y-auditor` → `@tsh-product-testing:a11y-auditor`
  - Wrong: `tsh-a11y-auditor` → `@tsh-product-testing:tsh-a11y-auditor`
- Agent filename matches its frontmatter `name`. Skill directory name *is* the
  skill name.
- **Skill names carry no framework version.** `implementing-nestjs-api`, not
  `implementing-nestjs-11-api`. A skill name is its invocation command, so pinning
  a dependency's major forces a rename on every upgrade — breaking docs, muscle
  memory, and any `enabledPlugins` entry, with no deprecation mechanism. Put the
  version in the `description` and in a **Version Baseline** block at the top of
  `SKILL.md` that tells Claude to check `package.json` and stop if the project is
  outside the supported range. The plugin's `version` field is the only version
  this repo tracks.
- **Keep skill names tech-qualified.** `implementing-nestjs-api`, not
  `implementing-api`. Namespacing makes `tsh-stack-java:implementing-api` and
  `tsh-stack-nodejs:implementing-api` both legal, but the model routes on
  descriptions, and two near-identical ones are a coin flip. It applies with extra
  force to the two TypeScript configuration skills, which are near-twins by design:
  `configuring-typescript-for-frontend` and `configuring-typescript-for-nodejs`
  name their target because nothing else would tell them apart. This applies in
  `tsh-core` too: `managing-git-worktrees`, not `managing-worktrees` — naming the
  tool keeps the *name-the-tool* admission test visible in the directory listing,
  and "worktree" alone collides with monorepo *workspaces*.
  `writing-technical-documents` names no tool because it is the one admitted
  exception; it names the artifact class instead, which does the same routing work.
  Do not treat its presence in the listing as permission to skip the test.

## Hard rules

1. **Only `plugin.json` goes inside `.claude-plugin/`.** `agents/`, `skills/`,
   `hooks/` and everything else live at the plugin root. Putting them under
   `.claude-plugin/` is the single most common plugin bug and fails silently.
2. **A new plugin must be added to `.claude-plugin/marketplace.json`** or nobody
   can install it. The marketplace file is the catalog; the plugin directory alone
   is invisible. Landing the entry only makes the plugin *installable* — teammates
   who already added the marketplace keep reading their cached clone of the
   catalog, so a new plugin stays absent from **Discover** and `/plugin install`
   reports it doesn't exist until they run `/plugin marketplace update
   tsh-agentic-collections`. Neither `/plugin update` nor a `version` bump reaches
   them, since a new plugin has no installed version to compare against; announce
   a new plugin with the marketplace-update command attached.
3. **Bump `version` in the plugin's `plugin.json` when shipping a change — that
   file only.** Claude Code resolves a plugin's version from `plugin.json` first,
   then the marketplace entry, then the commit SHA. Because `plugin.json` always
   wins, `marketplace.json` deliberately carries no `version` field; adding one
   back would shadow nothing and mislead the next contributor. Teammates receive
   an update only when this string changes — push without bumping it and
   `/plugin update` reports "already at the latest version", with no error to
   explain why nothing arrived.

   **How much to bump**, per plugin:

   | Bump | When |
   | :-- | :-- |
   | `patch` | Wording, clarifications, a fix — no change to what the plugin can do |
   | `minor` | A new skill or agent, or an existing one gains a capability |
   | `major` | A skill or agent is renamed or removed, or a non-negotiable rule reverses in a way an existing workflow could depend on |

   Renames are `major` because there is no deprecation mechanism: the name is the
   invocation command, so it breaks docs, muscle memory and `enabledPlugins`
   entries at once (see [Naming](#naming)).

   **Bump in the same commit as the change, and add a `CHANGELOG.md` entry to that
   plugin in the same commit too.** There is no release step to separate them from
   — the marketplace serves whatever is on `main`, so merging *is* releasing. Use
   [Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/) with **no
   `[Unreleased]` section**, for the same reason: nothing sits unreleased. Create a
   plugin's `CHANGELOG.md` at its first version bump; don't scaffold empty ones.
   [`plugins/tsh-core/CHANGELOG.md`](plugins/tsh-core/CHANGELOG.md) is the worked
   example.

   Nothing in Claude Code surfaces release notes, so link the changelog from the
   plugin's `README.md` and attach the link when you announce a bump. Which command
   teammates need depends on what changed: an **existing** plugin reaches them with
   `/plugin update`, a **brand-new** plugin needs
   `/plugin marketplace update tsh-agentic-collections` first — see rule 2.
4. **A `CLAUDE.md` inside a plugin is not loaded.** Claude Code ignores it. To ship
   instructions that reach Claude's context, write a skill. Per-plugin human docs
   go in that plugin's `README.md`.
5. **Plugin agents may not declare `hooks`, `mcpServers`, or `permissionMode`.**
   Claude Code rejects those fields in plugin-shipped agents for security reasons.
6. **Keep `templates/` out of the plugins.** It sits at the repo root precisely so
   Claude Code never loads the examples as real components.
7. **Cross-link only inside your own plugin.** Reference bundled files as
   `./references/<topic>.md` from `SKILL.md`, or `${CLAUDE_PLUGIN_ROOT}/…` for
   files shared between skills of the same plugin — Claude Code substitutes
   `${CLAUDE_PLUGIN_ROOT}` and `${CLAUDE_SKILL_DIR}` in plugin skill markdown.
   Never path into another plugin: it may not be installed, and the failure is a
   silent dead link rather than an error. Knowledge that must cross-link has to be
   co-located; duplicate the file if two plugins genuinely need it.
8. **Progressive disclosure above ~150 lines.** `SKILL.md` carries only the
   frontmatter, applicability and precedence, the non-negotiable rules table, a
   **Reference Loading** table, and the procedure. Detail goes in `references/`,
   one concern per file, ≤300 lines each. Two rules make this actually work:
   - The Reference Loading table needs a **"Load when"** column. A bare list of
     links gets skimmed; a trigger condition per row gives the model a predicate
     to evaluate. Pair it with an imperative at the point of use ("read
     `./references/x.md` before writing any controller") — instruction-following
     beats table lookup, and the two reinforce each other.
   - A rule that blocks review belongs in `SKILL.md` even if a reference also
     explains it. `SKILL.md` is what's in context when the model reads no
     references at all.
9. **`tsh-core` admits by elimination and evidence, and every addition discloses
   its cost.** A contribution lands there only if it fails both routing questions,
   wraps a named tool rather than a TSH opinion, and the PR says which three of the
   five disciplines would invoke it in a normal month. `writing-technical-documents`
   is the single named exception to the name-a-tool test; do not read it as licence
   to add a second. There is no cap on skill count, but the PR reports the
   plugin's routing footprint before and after. Ties go to a discipline plugin.
   This is a hard rule and not just prose because it is the one convention whose
   violation is invisible at review time — a wrongly-placed skill loads fine,
   validates fine, and simply taxes everyone's context forever. See
   [Core plugin admission](#core-plugin-admission).

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
