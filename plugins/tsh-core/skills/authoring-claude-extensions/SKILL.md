---
name: authoring-claude-extensions
description: "Decides which Claude Code extension a need calls for — skill, subagent, hook, or plugin — and then writes it. Use when building or changing any of those four, when Claude should do something automatically or every time, when a workflow keeps getting pasted into chat, or when a setup has to be shared across repositories."
when_to_use: "Trigger on: creating or editing a skill, subagent, hook or plugin; \"make Claude do X automatically\"; \"this should happen every time\"; a procedure pasted into chat repeatedly; a side task flooding the conversation; packaging a setup for a second repository or a marketplace; or any question of the form \"should this be a skill or a hook / a rule / an agent?\""
---

# Authoring Claude Code extensions

Two jobs, in order: **decide which primitive the need calls for**, then **build that
primitive correctly**. The first job is where the expensive mistakes happen — a
correctly written extension in the wrong primitive still fails, and it fails
invisibly, because the file looks right in review.

## Scope, and the one boundary that matters

This skill covers **skills, subagents, hooks, and plugins**.

> **If the answer is a memory file — `CLAUDE.md`, a `.claude/rules/` file, or a
> decision record — stop and use `managing-claude-context`.** That skill owns the
> memory layer; this one owns the things you build.

Not covered at all: writing an MCP server, agent teams, code intelligence,
artifacts. Bundling an existing MCP server in a plugin is a one-line `.mcp.json` at
the plugin root; the packaging reference names it and goes no further.

## Applicability and Precedence

Read what the repository already has before adding to it. An existing skill, agent or
hook is a statement of team intent — extend it in place rather than adding a second
one beside it. Where the repository has its own conventions for naming, layout or
packaging, those win over this skill's defaults.

**Claude Code's own documentation outranks this skill.** These mechanics ship on
Claude Code's release cadence, and every reference here is a snapshot with its sources
and a verification date at the bottom. Where the two disagree, follow the docs and fix
the reference.

## Explicit Exclusions

This skill does not:

- write product code, tests, or infrastructure
- decide what a team's workflow *should be* — it packages workflows the team already
  has, and asks when the workflow is ambiguous rather than inventing one
- author `CLAUDE.md`, `.claude/rules/`, or decision records — see
  [`managing-claude-context`](../managing-claude-context/SKILL.md)
- configure MCP servers or permissions
- mark anything as enforced that the team has not agreed to enforce

## Choose the primitive

Route on **what just happened to you**, not on the artifact you already have in mind.

| What just happened | Build this |
| --- | --- |
| Claude got a convention or command wrong twice | `CLAUDE.md` → `managing-claude-context` |
| **You need guidance while _creating_ a file that does not exist yet** | **A skill.** A path-scoped rule fires on *read*, so it can never reach you here |
| You need guidance while _editing_ files that already exist, and only some of them | A path-scoped rule → `managing-claude-context` |
| You pasted the same multi-step procedure into chat for the third time | A skill |
| You keep typing the same prompt to start a task | A skill, user-invocable |
| A side task floods the conversation with output you will not read again | A subagent |
| You need several independent opinions, or work that reads many files | A subagent |
| It must happen every time, the same way, without Claude deciding | A hook |
| Claude keeps ignoring an instruction that must always hold | A hook — not stronger wording |
| A second repository needs the same setup | A plugin |

Row two is the one people get wrong, and it is worth stating as its own rule: **the
question is not only what the guidance is *about*, it is *when* it is needed.**
Guidance about `SKILL.md` files that is needed while writing a new one is a skill,
even though a rule scoped to `**/SKILL.md` looks like a perfect fit.

Read [`./references/choosing-the-primitive.md`](./references/choosing-the-primitive.md)
**before writing anything** when the table gives more than one plausible answer.

## Non-negotiable Rules

| Severity | Rule |
| --- | --- |
| MUST | Decide the primitive before writing a line. Ask *when* the guidance is needed, not only what it is about. |
| MUST | Route creation-time guidance to a skill. A path-scoped rule fires only when Claude **reads** a matching file, so guidance for authoring a file that does not exist yet never loads. |
| MUST | Write `description` the way a person would phrase the request, not the way the artifact is filed. It is the only thing routing sees. |
| NEVER | Ship two extensions whose descriptions overlap. Routing between near-identical descriptions is a coin flip, and the loser is silently never invoked. |
| MUST | Use a hook, not an instruction, when something must hold regardless of what Claude decides. Instructions are context, not enforcement. |
| NEVER | Declare `hooks`, `mcpServers` or `permissionMode` in a **plugin-shipped** subagent. Claude Code ignores those fields there. |
| MUST | Keep `SKILL.md` under ~150 lines and move detail into `references/`, one concern per file, ≤300 lines each. |
| MUST | Give every Reference Loading table a **Load when** column, and repeat the trigger as an imperative at the point of use. |
| MUST | Verify the extension actually loaded and actually routes before calling the work done. Confirm with `/context`, and test the description with a request that does not name it. |
| NEVER | Set a status, enable a hook, or mark something enforced that the team has not agreed to. |

## Reference Loading

| Reference | Load when | Covers |
| --- | --- | --- |
| [Choosing the primitive](./references/choosing-the-primitive.md) | The routing table gives more than one plausible answer, every time | The full predicate: timing vs scope, trigger determinism, context cost, the read-not-write trap and its symptom, skill vs subagent, hook vs instruction |
| [Authoring a skill](./references/authoring-a-skill.md) | Writing or restructuring any `SKILL.md` | Frontmatter, writing a `description` that routes, `disable-model-invocation` and `user-invocable`, progressive disclosure, references, arguments |
| [Authoring a subagent](./references/authoring-a-subagent.md) | Writing or changing a subagent | The frontmatter field set, `tools` and `disallowedTools`, what loads at startup, precedence across scopes, the plugin-shipped restrictions |
| [Authoring a hook](./references/authoring-a-hook.md) | Writing a hook, or deciding whether something needs enforcing | Events and which ones block, matchers, handler types, exit codes and JSON output, where hooks are registered |
| [Packaging a plugin](./references/packaging-a-plugin.md) | Bundling extensions for another repository or a marketplace | Directory layout and the manifest trap, `${CLAUDE_PLUGIN_ROOT}`, namespacing, marketplaces, versioning and distribution |

## Procedure

**Step 1 — Read what exists.** List the skills, agents and hooks already present at
project, user and plugin scope. Run `/context` to see what loads today. An extension
that duplicates one already installed makes both worse, because routing has to pick.

**Step 2 — Choose the primitive.** Apply the table above. When two rows both fit, read
[`choosing-the-primitive.md`](./references/choosing-the-primitive.md) — the deciding
questions are *when is this needed*, *must it be guaranteed*, and *whose context pays*.
If the answer is a memory file, stop here and hand off to `managing-claude-context`.

**Step 3 — Confirm the trigger exists.** Name the moment the extension will fire, and
check that moment is real. A hook needs an event that actually occurs; a path-scoped
rule needs a file that will actually be read; a skill needs a request someone will
actually phrase. **An extension whose trigger never occurs is indistinguishable from
one that was never written.**

**Step 4 — Write it.** Read the reference for that primitive first. Write the routing
surface — `description`, `when_to_use`, matcher — before the body, because that is
what decides whether the body is ever reached.

**Step 5 — Verify it loads and routes.** Start a session and run `/context`. Then test
the routing with a request phrased the way a user would phrase it, **without naming
the extension**. If it does not route, the `description` is wrong; fix that before
anything else.

**Step 6 — Report.** Say which primitive you chose and which you rejected, and why.
The rejected option is the part a reviewer needs in order to disagree.

## Self-check Before Handoff

```text
- [ ] The primitive was chosen deliberately, and the rejected alternative is named
- [ ] Timing was considered, not just subject matter
- [ ] `description` is phrased the way a person would ask, and does not overlap an existing one
- [ ] The trigger has been shown to occur — a real event, a file that gets read, a request someone makes
- [ ] Nothing enforced that the team has not agreed to enforce
- [ ] No plugin-shipped subagent declares `hooks`, `mcpServers` or `permissionMode`
- [ ] `/context` confirms it loaded, and an un-named request routes to it
- [ ] Memory-file work was handed to `managing-claude-context`, not done here
```
