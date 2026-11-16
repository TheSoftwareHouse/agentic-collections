---
title: Discovering Technical Context
sidebar_label: discovering-technical-context
sidebar_position: 4
description: Establishes which conventions a change must follow before it is written, in priority order from the plan's persisted context to project instructions, codebase patterns and external documentation.
sources:
  - plugins/tsh-product-engineering/skills/discovering-technical-context/
sources_hash: "d34776298d5d5fd4a6b5c59ad4753d6a7d00b846a4b219938dbc1c092be088b5"
---

# Discovering Technical Context

**Plugin:** [`tsh-product-engineering`](/docs/plugins/tsh-product-engineering/)  
**Invoke:** `/tsh-product-engineering:discovering-technical-context`  
**Used by:** the agents [`software-engineer`](/docs/plugins/tsh-product-engineering/agents/software-engineer), [`ui-engineer`](/docs/plugins/tsh-product-engineering/agents/ui-engineer) and [`code-reviewer`](/docs/plugins/tsh-product-engineering/agents/code-reviewer) preload it. The skills [`creating-implementation-plans`](/docs/plugins/tsh-product-engineering/skills/creating-implementation-plans) (step 2 of its procedure), [`debugging-code`](/docs/plugins/tsh-product-engineering/skills/debugging-code), [`reviewing-code`](/docs/plugins/tsh-product-engineering/skills/reviewing-code) and [`orchestrating-feature-implementation`](/docs/plugins/tsh-product-engineering/skills/orchestrating-feature-implementation) reference it.

A systematic way to learn how a project does things before changing it, so new code is consistent with what exists and conventions are followed rather than reinvented. The output is often persisted into a plan's Technical Context section, where it saves every later agent from rediscovering the same facts.

Use it before implementing a feature or fix in code you have not worked in recently, before writing tests in an unfamiliar project, when two parts of the repository disagree on a convention, and when filling the Technical Context of an implementation plan. The skill is itself a precedence rule: project instructions outrank existing patterns, which outrank industry best practice. It never overrides an explicit instruction from the user.

## Key Areas

| Area | Coverage |
| :-- | :-- |
| **Persisted context first** | If the plan's Technical Context is populated, it is used as-is and only what it does not cover is re-discovered |
| **Project instructions** | The root `CLAUDE.md` and nested ones near the touched files, path-scoped rules under `.claude/rules/`, decision records, and `CONTRIBUTING.md` or equivalent. The primary source for coding standards, architecture and layering, stack versions, testing strategy and naming. A project's own verification or security-invariant skill, named in `CLAUDE.md`'s `tsh:project-checks` block or in the skill listing, is read too, as the source for verification commands, their boundaries and the project's security rules |
| **Existing codebase patterns** | When instructions are silent, the nearest similar implementation is replicated: architecture, style and idiom, error handling and validation, testing, persistence, API surface and configuration |
| **Exact dependency versions** | The project's manifest is checked for exact versions before any external documentation is consulted |
| **External documentation** | Only when neither instructions nor codebase answer, for example in a greenfield project. Official docs for the pinned versions are read, and the decision is documented so it becomes the project's pattern |
| **No new patterns** | A new pattern is never introduced unless the user or the plan explicitly asks for one |

## How it works

The skill follows a five-step checklist:

0. **Persisted context in the plan.** Use a populated `*.plan.md` Technical Context and skip to step 4.
1. **Project instructions.** Read what is present.
2. **Existing codebase patterns.** Find the nearest similar implementation for whatever the instructions leave unstated.
3. **External documentation**, only if needed.
4. **Apply the decision hierarchy:**

| Context available | Action |
| :-- | :-- |
| Project instructions cover it | Follow them strictly, because they outrank general best practice |
| Instructions silent, codebase has a pattern | Mirror the existing pattern exactly |
| Neither exists | Apply documented best practice and record the decision for the next person |

## Related skills

- [`creating-implementation-plans`](/docs/plugins/tsh-product-engineering/skills/creating-implementation-plans) persists what this skill discovers into the plan's Technical Context.

## Source

[`plugins/tsh-product-engineering/skills/discovering-technical-context/SKILL.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-product-engineering/skills/discovering-technical-context/SKILL.md)
