---
name: capturing-project-checks
description: "Writes a repository's own verification and security-invariant skills into `.claude/skills/` and points `CLAUDE.md` at them: which checks each kind of change needs, the full pre-merge gate as CI runs it, the boundaries every check must respect, and the project's non-negotiable security rules, each traced to its source. Review, audit, planning and debugging then apply the project's own bar even without a plan. Use when checks are re-discovered every session, nobody has written down how to verify a change, or the project's security rules live in people's heads."
when_to_use: "Trigger on: 'write down how to verify changes in this repo', 'which checks should run for which change', capturing the project's PR gate or its definition of verified, recording client or project security rules so every review applies them, or repairing a project verification or security-review skill that drifted from CI. Setting up `CLAUDE.md` and path-scoped rules in general is tsh-core's managing-claude-context; writing any other skill, hook or subagent is tsh-core's authoring-claude-extensions; running a review is reviewing-code; a security audit is auditing-application-security."
---

# Capturing Project Checks

Every skill in this plugin defers to the project's own commands and security rules,
but a project rarely writes them down where a session can find them. Without a plan,
each review, fix or audit re-derives the checks from scratch, and the project's
security rules stay in people's heads. This skill records both as **project skills**
— procedures, so a skill rather than `CLAUDE.md`, by tsh-core's own layer predicate —
and names them in `CLAUDE.md` so every session finds them.

It records what the repository already holds. It does not decide what the checks or
the rules *should* be.

## Applicability and Precedence

- An existing project skill that already covers verification or security is
  **revised in place** under its own name, never replaced by a new one. When its
  `SKILL.md` only points at another file, edit the file that holds the content.
  Repair changes facts, not shape: another tool may read that file.
- What CI runs is the source of truth for the full gate. A local command that runs
  less than CI is recorded as a subset, never as the gate.
- `CLAUDE.md` hard rules, `Accepted` decision records, `SECURITY.md` and written
  client requirements are the sources of security invariants. The code shows how
  things are done today, not what must stay true; an invariant seen only in code is a
  candidate the user confirms.
- `CLAUDE.md` and `.claude/rules/` in general belong to `managing-claude-context`.
  This skill writes only its own fenced block there.
- **A repository attached to a project knowledge base** (a `tsh:project-context`
  block in `CLAUDE.md` or `CLAUDE.local.md`) keeps its decision records there. This
  skill reads them and writes nothing in the knowledge base: every invariant stays in
  the repository's own skill, the ones the team confirms as project-wide are marked,
  and a draft for the project's `<slug>-shared` plugin goes in the report for a
  person to add. Read
  [`security-invariants-skill.md`](./references/security-invariants-skill.md) §6.
- **A repository the team may not commit to** (the block is in `CLAUDE.local.md`
  and the plugin entry in `.claude/settings.local.json`: a client's repository) gets no tracked file from this skill. Ask whether the files
  may be committed here. On "keep local", write the skills, put the pointer block in
  `CLAUDE.local.md` beside the `tsh:project-context` block, which stays byte for
  byte, and list every path written in `.git/info/exclude`. With no answer, write
  nothing and put both drafts in the report.

## Non-negotiable Rules

| Severity | Rule |
| --- | --- |
| MUST | Read `CLAUDE.md`, `CLAUDE.local.md`, `.claude/settings.json` and `.claude/settings.local.json` from disk before anything else. The fence markers are HTML comments, which are stripped from the copy already in context, so only the file shows them. A `tsh:project-context` block, or an enabled `<slug>-shared@<slug>-context` plugin, marks an attached repository; found only in the `.local` files, it marks one the team may not commit to. |
| MUST | Inventory before writing: `.claude/skills/`, an existing `tsh:project-checks` block, CI workflows, task runners, test configuration, `docs/decisions/`, `SECURITY.md`. Report it before changing anything. |
| MUST | Read a command before running it: the script or job it expands to, the environment it resolves (`.env`, exported variables, CI secrets) and the traps `CLAUDE.md` or the README name. A pipeline job that deploys, publishes or applies is never part of the gate and is never run. |
| MUST | Run every check command before writing it down, unless it is destructive, costs money, needs a service or credential that is not available, or reaches a real external system or a shared environment. Such a command is written with what it needs and marked not run in the report. |
| NEVER | Run a check against production, a real third-party service or a shared environment, or start a long-running server, to prove a command works. A database or emulator counts as local only when the project's own tooling starts it. |
| NEVER | Invent a check, a boundary or an invariant. Each one traces to a file, or to a confirmation the team gave during capture; anything inferred only from code is proposed to the user and written only on a yes. |
| NEVER | Copy the universal security baseline or generic OWASP advice into the invariants skill. It holds only what is specific to this project; the baseline already runs in every review. |
| NEVER | Commit, stage or push. Write the files and leave them for the team to review. In a project knowledge base, write nothing and run no git: a change there belongs to that knowledge base's own process and its owners. |
| MUST | Keep each generated skill under ~100 lines, model-invocable, with a description that names the project and what the skill covers. |
| MUST | Write the `CLAUDE.md` pointer only inside the `tsh:project-checks` block, paths in backticks, never an `@` import, and rewrite that block whole on every run. |
| MUST | End with a report: created, repaired, left alone; commands run and not run; invariants confirmed, declined and still open; in an attached repository, the decision records read or not read and the shared-plugin draft. Present the result as a proposal. |

## Reference Loading

| Reference | Load when | Covers |
| --- | --- | --- |
| [Verification skill](./references/verification-skill.md) | Step 2, every run | Where checks come from, mapping change types to checks, the full gate, boundaries, the generated skill's template |
| [Security invariants skill](./references/security-invariants-skill.md) | Step 3, every run | Sources of invariants, the confirm-before-writing rule for code-only candidates, the generated skill's template |

## Procedure

```text
Project checks:
- [ ] 1. Inventory
- [ ] 2. Verification skill
- [ ] 3. Security invariants skill
- [ ] 4. CLAUDE.md block
- [ ] 5. Verify and report
```

**Step 1 — Inventory.** List what the Non-negotiable Rules name, and note any project
skill whose description covers verifying changes or security review. Each one found
switches its step to repair mode: compare it with the sources, correct what drifted,
keep what still holds.

**Step 2 — Verification skill.** Read
[`verification-skill.md`](./references/verification-skill.md) before deriving
anything. Default location: `.claude/skills/verifying-changes/SKILL.md`.

**Step 3 — Security invariants skill.** Read
[`security-invariants-skill.md`](./references/security-invariants-skill.md) first.
Default location: `.claude/skills/reviewing-security-invariants/SKILL.md`. In an
attached repository follow §6 of the reference: read the decision records through
`/tsh-product-management:navigating-project-context`, or say they were not read when
that skill is not in this session; keep every invariant in the repository's skill;
ask in one batch which hold project-wide, mark those, and put the shared-plugin draft
in the report. When no source yields an invariant and the user confirms none, write
no skill and say so — an empty invariants skill is noise.

**Step 4 — `CLAUDE.md` block.** Add or rewrite this block near the end of root
`CLAUDE.md`, after the orientation content, naming the skills by their actual names
and paths and dropping the line for a skill that does not exist. When there is no
`CLAUDE.md`, create one holding only this block and tell the user that
`/tsh-core:managing-claude-context` writes the rest; the block alone is not a
`CLAUDE.md`.

```markdown
<!-- tsh:project-checks START — only /tsh-product-engineering:capturing-project-checks edits this block. -->
Verifying a change: the `verifying-changes` skill (`.claude/skills/verifying-changes/SKILL.md`); its checks and boundaries apply to every change, with or without a plan. Security invariants: the `reviewing-security-invariants` skill (`.claude/skills/reviewing-security-invariants/SKILL.md`); they outrank generic security checklists. When CI, task runners or security rules change, re-run `/tsh-product-engineering:capturing-project-checks`; without that plugin, update the two skills by hand in the same change.
<!-- tsh:project-checks END -->
```

**Step 5 — Verify and report.** Confirm each file is where the block says, then
re-read each generated skill against the rules above. Skills load at session start,
so ask the user to confirm with `/context` in a fresh session. Report in the shape
the last rule names. A second run on an unchanged repository must find nothing to
change and ask nothing again: a command already recorded and unchanged at its source
is not re-run, an invariant whose source is a team confirmation is kept as it stands,
and declined candidates and project-wide marks are read back from the skill.

## Related Skills

Ships in this plugin — if this skill loaded, it is installed.

- [`discovering-technical-context`](../discovering-technical-context/SKILL.md) —
  reads the skills this one writes as project instructions, so plans carry their
  commands.
- [`reviewing-code`](../reviewing-code/SKILL.md) and
  [`auditing-application-security`](../auditing-application-security/SKILL.md) —
  apply the verification checks and the security invariants.
