---
title: Capturing Project Checks
sidebar_label: capturing-project-checks
sidebar_position: 0.5
description: Writes a repository's own verification and security-invariant skills into .claude/skills/ and names them in CLAUDE.md, so reviews, plans, fixes and audits apply the project's own bar even without a plan.
sources:
  - plugins/tsh-product-engineering/skills/capturing-project-checks/
sources_hash: "d273cc151bf58d80a0d5ca919d64c87149e65103d03afaa4188f27b349932bbb"
---

# Capturing Project Checks

**Plugin:** [`tsh-product-engineering`](/docs/plugins/tsh-product-engineering/)  
**Invoke:** `/tsh-product-engineering:capturing-project-checks`  
**Used by:** [`/tsh-core:init`](/docs/plugins/tsh-core/skills/init) invokes it as its fourth step where this plugin is installed; it can also be run directly. The skills it writes are read by [`discovering-technical-context`](/docs/plugins/tsh-product-engineering/skills/discovering-technical-context), [`reviewing-code`](/docs/plugins/tsh-product-engineering/skills/reviewing-code) and [`auditing-application-security`](/docs/plugins/tsh-product-engineering/skills/auditing-application-security).

Every skill in this plugin defers to the project's own commands and security rules, but a project rarely writes them down where a session can find them. Without a plan, each review, fix or audit re-derives the checks from scratch, and the project's security rules stay in people's heads. This skill records both as **project skills** and names them in `CLAUDE.md` so every session finds them. It records what the repository already holds; it does not decide what the checks or the rules should be.

Use it when checks are re-discovered every session, nobody has written down how to verify a change, or the project's security rules live in people's heads. It also repairs a project verification or security-review skill that drifted from CI; repair changes facts, not shape, because another tool may read that file. Setting up `CLAUDE.md` and path-scoped rules in general is [`managing-claude-context`](/docs/plugins/tsh-core/skills/managing-claude-context) in `tsh-core`, and writing any other skill, hook or subagent is [`authoring-claude-extensions`](/docs/plugins/tsh-core/skills/authoring-claude-extensions).

## What it writes

| Artifact | Default location | Holds |
| :-- | :-- | :-- |
| **Verification skill** | `.claude/skills/verifying-changes/SKILL.md` | Which checks each kind of change needs, the full gate as CI runs it, and the boundaries every check must respect |
| **Security invariants skill** | `.claude/skills/reviewing-security-invariants/SKILL.md` | The project's non-negotiable security rules, each citing its source, plus the open decisions a change must not settle silently |
| **`tsh:project-checks` block** | root `CLAUDE.md`, near the end | A short pointer naming both skills by their actual names and paths, and saying to re-run this skill when CI, task runners or security rules change |

In a repository attached to a project knowledge base (a `tsh:project-context` block, from `tsh-product-management`'s `initializing-project-context`), the decision records are read from the knowledge base through `navigating-project-context`, and the invariants that hold for every repository of the project go to the project's own `<slug>-shared` plugin as `<slug>-security-invariants`, under that plugin's sharing rule: Markdown only, a version bump and a changelog line, written through the knowledge base's own write flow with each git step after the person's yes, never into the person's own clone. Verification stays in the code repository, because CI is per repository. The repository's own invariants skill names the shared one.

An existing project skill that already covers verification or security is revised in place under its own name. When no source yields a security invariant and the team confirms none, no invariants skill is written. When there is no `CLAUDE.md`, one is created holding only the block, and the user is told that `managing-claude-context` writes the rest.

## Key rules

| Area | Coverage |
| :-- | :-- |
| **CI is the gate** | The CI jobs that must pass before merge are the source of truth for the full gate. Jobs that deploy, publish, apply infrastructure or release are never part of it and are never run. A local command that runs less is recorded as a subset, never as the gate |
| **Read, then run** | Each command is read before it runs: the script or job it expands to, the environment it resolves (`.env`, exported variables, CI secrets) and the traps `CLAUDE.md` or the README name. Then every check command is run before it is written down, unless it is destructive, costs money, needs an unavailable service or credential, or reaches a real external system or a shared environment (one of the project's own; a read of a public package registry runs like any other check). Such a command is written with what it needs and reported as not run |
| **Safe boundaries** | Nothing runs against production, a real third-party service or a shared environment, and no long-running server is started to prove a command. A database or emulator counts as local only when the project's own tooling starts it |
| **Sourced invariants** | Each invariant traces to a file: written client requirements, `CLAUDE.md` hard rules, `Accepted` decision records, `SECURITY.md`, guard scripts in CI, or past pen-test remediations. A rule seen only in code is proposed to the team and written only on a yes, with that confirmation as its source; a later run keeps it as it stands |
| **No baseline copy** | Generic OWASP advice stays out. The universal baseline already runs in every review, so the invariants skill holds only what is specific to the project |
| **Nothing committed** | Files are written for the team to review. Nothing is staged, committed or pushed |

A skill is applied when a session loads it: the `CLAUDE.md` block makes every session aware of it, and the plugin's review, planning, debugging and audit skills load it by rule. A guarantee that holds whatever the session decides is a hook's job, and the verification skill is what such a hook would run; no hook ships here.

Every generated verification skill carries four boundaries: never run a check against production or a real third-party service, never print a secret or `.env` value, never change code, tests or thresholds to hide a failure the change did not cause, and never claim a check passed that was not run.

## How it works

1. **Inventory** `.claude/skills/`, root `CLAUDE.md`, CI workflows, task runners, test configuration, decision records and `SECURITY.md`. A project skill found for verification or security switches its step to repair mode.
2. **Verification skill:** checks from CI workflows first, then task runners, git hooks, test configuration and the project's written instructions, mapped to the kinds of change the repository actually has.
3. **Security invariants skill:** invariants from their sources, grouped by boundary, with code-only candidates confirmed in one batch.
4. **`CLAUDE.md` block:** added near the end or rewritten whole on every run.
5. **Verify and report:** each file is confirmed to be where the block says; skills load at session start, so the user confirms with `/context` in a fresh session. The report lists what was created, repaired and left alone; commands run and not run; and invariants confirmed, declined and still open. A second run on an unchanged repository finds nothing to change.

## Reference Loading

| Reference | Load when |
| :-- | :-- |
| `verification-skill.md` | Step 2, every run |
| `security-invariants-skill.md` | Step 3, every run |

## Related skills

- [`discovering-technical-context`](/docs/plugins/tsh-product-engineering/skills/discovering-technical-context) reads the skills this one writes as project instructions, so plans carry their commands.
- [`reviewing-code`](/docs/plugins/tsh-product-engineering/skills/reviewing-code) and [`auditing-application-security`](/docs/plugins/tsh-product-engineering/skills/auditing-application-security) apply the verification checks and the security invariants.

## Source

[`plugins/tsh-product-engineering/skills/capturing-project-checks/SKILL.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-product-engineering/skills/capturing-project-checks/SKILL.md)
