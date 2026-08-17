---
name: contributing-a-plugin-component
description: "Places a new agent, skill or plugin in this marketplace — which plugin owns it, whether it clears the tsh-core admission bar, and what to name it. Use when adding or moving anything under plugins/, before writing the file."
when_to_use: "Trigger on: adding a skill or agent to any tsh-* plugin, creating a new plugin, moving a component between plugins, or any question of the form \"where does this belong in this repo?\""
---

# Contributing a plugin component

This skill answers **where it goes and what it is called**. It does not teach how to
write a `SKILL.md` or an agent file — that belongs to
`/tsh-core:authoring-claude-extensions`, which this skill hands off to at step 4.
(That skill ships in the `tsh-core` plugin; install it if the command is not
available.)

Run this **before creating the file.** The conventions below live in
`.claude/rules/`, which fires when Claude *reads* a matching file — so it cannot reach
you while you are creating one. That is the whole reason this skill exists.

## Step 1 — What are you adding?

| | Use when | Invoked as |
| :-- | :-- | :-- |
| **Agent** | Self-contained work whose intermediate reasoning should stay out of the conversation — audits, reviews, investigations. It hands back a report. | `@tsh-product-testing:a11y-auditor` |
| **Skill** | A procedure the main agent should follow inline, with full access to what the conversation knows. It changes how the conversation proceeds. | `/tsh-product-testing:audit-page` |
| **Plugin** | Neither fits an existing plugin's scope — see step 2 before concluding this. | — |

## Step 2 — Which plugin owns it?

Apply the routing predicate in `CLAUDE.md` — *ask in order, stop at the first yes*.
It is already in context; do not restate it here.

Then, depending on where it lands:

- **`tsh-core`** → read `.claude/rules/core-plugin-admission.md` **now**, before
  writing anything. Admission is by elimination *plus evidence*: the PR must name
  which three of the five disciplines would invoke it in a normal month, and report
  the plugin's routing footprint before and after. **Ties go to a discipline plugin.**
- **`tsh-stack-*`** → read `.claude/rules/stack-plugin-conventions.md`. A stack is a
  runtime target, not a language, and duplication between stack plugins is deliberate.
- **A discipline plugin** → no extra gate. This is the default, and it is meant to be.
- **A new plugin** → it also needs an entry in `.claude-plugin/marketplace.json`, or
  nobody can install it. See `.claude/rules/plugin-manifests-and-marketplace.md`.

## Step 3 — Name it

- Kebab-case, **without** a `tsh-` prefix — the plugin already namespaces it.
- Agent filename matches its frontmatter `name`. A skill's directory name *is* its name.
- **No framework version in the name**: `implementing-nestjs-api`, never
  `implementing-nestjs-11-api`. The name is the invocation command, so a pinned major
  forces a rename on every upgrade, and a rename is a `major` bump.
- **Keep it tech-qualified**: `implementing-nestjs-api`, not `implementing-api`. The
  model routes on descriptions, and two near-identical ones are a coin flip.

## Step 4 — Write it

Hand off to **`/tsh-core:authoring-claude-extensions`** for the mechanics: frontmatter,
writing a `description` that routes, progressive disclosure above ~150 lines, the
Reference Loading table's **Load when** column, and the fields a plugin-shipped agent
may not declare.

Two constraints from this repo that apply while writing:

- **Cross-link only inside your own plugin.** `./references/<topic>.md`, or
  `${CLAUDE_PLUGIN_ROOT}/…` between skills of the same plugin. A path into another
  plugin is a silent dead link when that plugin is not installed.
- **A `CLAUDE.md` inside a plugin is not loaded.** Ship instructions as a skill;
  per-plugin human docs go in that plugin's `README.md`.

## Step 5 — Ship it

Invoke **`/releasing-a-plugin-change`**. Merging is releasing here, so the version
bump and the `CHANGELOG.md` entry land in the same commit as the change.

## Before opening the PR

```text
- [ ] The owning plugin was chosen with the CLAUDE.md predicate, not by feel
- [ ] If tsh-core: three disciplines named, routing footprint reported before and after
- [ ] Name is kebab-case, unprefixed, tech-qualified, carries no framework version
- [ ] A new plugin has a marketplace.json entry, and the announcement names
      `/plugin marketplace update tsh-agentic-collections`
- [ ] No cross-plugin links
- [ ] `claude plugin validate ./plugins/<name>` and `claude plugin validate .` pass
- [ ] Version bumped and CHANGELOG entry written, in this same commit
```
