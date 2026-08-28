# Routing a proposal

Read this once a candidate has cleared the evidence bar. Routing answers two questions:
**where would this artifact live**, and **who has to be told what** before it can be
built. A proposal that skips either is a wish rather than a work item.

## Where it would live

Two destinations, and the repository tells you which applies.

**A plugin in a marketplace** — the artifact is shared with other people or other
repositories. Path: `plugins/<plugin>/skills/<name>/`,
`plugins/<plugin>/agents/<name>.md`, or the equivalent for the primitive.

**Repo-local `.claude/`** — the artifact is specific to this one repository. Path:
`.claude/skills/<name>/`, `.claude/agents/<name>.md`, `.claude/rules/<name>.md`, or
`.claude/settings.json` for a hook.

Decide with this test, and state the answer in the proposal:

> **Would a second repository need this same thing?** If yes, it is a plugin artifact.
> If it depends on this repository's own layout, history or business domain, it is
> repo-local.

Being *useful* elsewhere is not the test — being *needed* elsewhere is. When the answer
is arguable, propose repo-local and say the plugin option was considered. A repo-local
artifact can be promoted later; an artifact shipped to everyone's context cannot be
quietly withdrawn.

## Which repository is this?

Check before naming a path, because guessing produces a target nobody can act on.

- A `.claude-plugin/marketplace.json` at the root means **this repository is a
  marketplace**. Plugin-bound candidates target a directory inside it, and the
  proposal must name that repository's own contribution and release procedure.
- A `.claude-plugin/plugin.json` and no marketplace file means **this is a single
  plugin**, likely consumed from elsewhere.
- Neither means **this is an ordinary project**. Plugin-bound candidates must name the
  marketplace repository they would go to, by name — and if you cannot determine which
  marketplace the team uses, say so and leave it as an open question in the proposal
  rather than inventing one.

## Naming the artifact

Propose a name, and expect it to be argued with. Constraints that apply everywhere:

- kebab-case, and no plugin prefix — the plugin namespaces it already
- no framework or dependency version in the name; the name is the invocation command,
  and pinning a major forces a rename on every upgrade
- specific enough that its description could not be confused with an existing
  artifact's, because routing between two similar descriptions is a coin flip

A repository may carry stricter naming rules of its own. Where it does, they win, and
the proposal should point at them instead of restating them.

## The handoff each primitive needs

Every proposal ends with the command that would build it. This is what makes the
document actionable rather than a note.

| Primitive proposed | Handoff |
| --- | --- |
| Skill, subagent, hook, plugin | `/tsh-core:authoring-claude-extensions` |
| `CLAUDE.md`, nested `CLAUDE.md`, `.claude/rules/` file | `/tsh-core:managing-claude-context` |
| Decision record | `/tsh-core:managing-decision-records` |
| A fix to an artifact that already exists | The same command as for its primitive, naming the existing file to change |

When the target is a marketplace or plugin repository, the handoff has **two** parts:
that repository's own placement and release procedure *first*, then the authoring
command. Marketplace repositories generally require a version bump and a changelog
entry in the same commit as the change, and a component added without them ships
silently broken. Name the requirement; do not attempt to satisfy it from a retro.

## What routing never does

- It never picks the primitive. That decision belongs to
  [`authoring-claude-extensions`](../../authoring-claude-extensions/SKILL.md) and has
  already been made by the time routing runs.
- It never creates the directory, the file, or the entry.
- It never edits a manifest, a marketplace catalog, or a changelog.
- It never decides that a shared artifact is worth everyone's context budget. It names
  the destination and the cost; a human weighs it.

## Disclose the cost

When the destination is a shared plugin, the proposal states what installing the
artifact costs the people who install it — a preloaded description that routing has to
consider for every request, an agent definition, or a hook that fires in every
repository. A destination named without its cost reads as free, and nothing shipped
into everyone's context is free.

If the target repository has its own admission bar for shared components, name it and
leave the test unanswered for a human. Arguing a candidate past someone else's
admission bar is not this skill's job.
