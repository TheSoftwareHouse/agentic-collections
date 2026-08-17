# Authoring a skill

Use this reference when writing or restructuring a `SKILL.md`. A skill is reusable
instructions that load into the current conversation — either because you invoked
`/name`, or because Claude matched your request against its `description`.

## 1. Where skills live

| Location | Scope | Invoked as |
| --- | --- | --- |
| `.claude/skills/<name>/SKILL.md` | This project | `/<name>` |
| `~/.claude/skills/<name>/SKILL.md` | All your projects | `/<name>` |
| `<plugin>/skills/<name>/SKILL.md` | Wherever the plugin is enabled | `/<plugin>:<name>` |

The directory name **is** the skill name. When the same name exists at several scopes,
one definition wins by priority; plugin skills are namespaced, so they never collide
with a project skill.

`.claude/commands/deploy.md` and `.claude/skills/deploy/SKILL.md` both produce
`/deploy` and behave the same way. The skill form adds a directory for supporting
files and frontmatter control over who may invoke it.

## 2. The `description` is the whole routing surface

Claude Code loads every skill's **name and description** into context at session
start, and routes on that text alone. The body is never consulted for the decision.

Write it the way a person phrases the request, not the way the artifact is filed:

| Weak | Routes |
| --- | --- |
| "Deployment documentation" | "Deploys the service to staging or production. Use when asked to deploy, ship, release, or roll back." |
| "Handles database things" | "Writes and reviews Postgres migrations. Use when adding a column, changing a schema, or debugging a failed migration." |

Rules that follow from how routing works:

- **Put the key use case first.** `description` and `when_to_use` are truncated
  together at 1,536 characters per skill.
- **Never let two descriptions overlap.** Routing between near-identical text is a
  coin flip, and the skill that loses is silently never invoked. If two skills are
  genuinely close, the names and the descriptions must both say what distinguishes
  them.
- **Budget is shared.** The listing scales at about 1% of the context window; when it
  overflows, descriptions are trimmed starting with the least-used skills. A verbose
  description degrades routing for skills you did not write.

## 3. Frontmatter

```yaml
---
name: releasing-a-service          # matches the directory name
description: "What it does, and when to use it — phrased as a person would ask."
when_to_use: "Trigger on: <concrete situations, comma separated>."
---
```

Optional fields worth knowing:

| Field | Use it for |
| --- | --- |
| `disable-model-invocation: true` | Side effects you want to time yourself — deploys, commits, anything that sends. Claude cannot invoke it, and its description costs nothing until you do. |
| `user-invocable: false` | Background knowledge that is not a meaningful command. Claude can load it; it stays out of the `/` menu. |
| `allowed-tools` | Tools the skill may use without per-use approval, for the turn that invoked it. |
| `context: fork` | Run the skill in an isolated subagent context instead of inline. |

Neither visibility flag is a security control. `disable-model-invocation: true` is what
actually removes a skill from Claude's context; `user-invocable: false` only hides it
from the menu.

## 4. Keep the body short

Once a skill loads, its content stays in context across turns, so every line is a
recurring cost. State what to do rather than narrating why.

**Above roughly 150 lines, split.** `SKILL.md` keeps only:

- frontmatter
- applicability and precedence, and explicit exclusions
- the non-negotiable rules table
- a Reference Loading table
- the procedure

Everything else moves to `references/`, one concern per file, **≤300 lines each**.

## 5. Two rules that make progressive disclosure work

**The Reference Loading table needs a "Load when" column.** A bare list of links gets
skimmed. A trigger condition per row gives the model a predicate it can evaluate:

| Reference | Load when | Covers |
| --- | --- | --- |
| `Rollback` → `./references/rollback.md` | A deploy failed, or you are planning one that might | The rollback procedure and its preconditions |

Then repeat the trigger as an imperative where it applies — "read
`./references/rollback.md` before touching a live deploy". Instruction-following beats
table lookup, and the two reinforce each other.

**A rule that blocks review stays in `SKILL.md`**, even if a reference explains it
fully. `SKILL.md` is what is in context when the model reads no references at all.

## 6. Supporting files

```text
.claude/skills/releasing-a-service/
├── SKILL.md
├── references/
│   └── rollback.md
└── scripts/
    └── check-health.sh
```

Reference bundled files as `./references/<topic>.md`. Inside a plugin, use
`${CLAUDE_PLUGIN_ROOT}/…` for files shared between skills of the same plugin, and
`${CLAUDE_SKILL_DIR}` for the skill's own directory — Claude Code substitutes both in
plugin skill markdown.

**Never path from one plugin into another.** The other plugin may not be installed, and
the failure is a silent dead link rather than an error.

## 7. Arguments

`$ARGUMENTS` carries everything typed after the command; `$1`, `$2` and named
arguments carry positional ones. Handle the empty case explicitly — a skill invoked
bare with no argument should ask, not guess.

To write a literal `$` before a digit or an argument name, escape it: `\$1.00`.

## 8. Verify it routes

Loading and routing are different failures, and only one of them is visible.

1. Start a session and run `/context`. The skill should appear in the listing.
2. Invoke it directly with `/<name>` to confirm the body is what you expect.
3. **Then make a request phrased the way a user would, without naming the skill.** If
   it does not load, the `description` is wrong — fix that before anything in the body.

Step 3 is the one people skip, and it is the one that decides whether the skill is ever
used by anyone but its author.
