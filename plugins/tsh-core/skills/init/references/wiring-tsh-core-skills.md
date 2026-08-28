# Wiring tsh-core skills into CLAUDE.md

Use this reference at init's Step 3, before writing or repairing the maintenance
section in a repository's root `CLAUDE.md`.

## 1. What this section is for

Init runs in one session; upkeep has to happen in every session after it. A
memory file rots unless something that loads in *those* sessions says how it is
maintained — the same reason `managing-claude-context` writes the
`Accepted`-only filter into the artifacts it generates rather than keeping it to
itself. The maintenance section carries two standing instructions into every
future session:

- when the project changes in a way the memory files should reflect, update them
  in the same change — and which skill does that;
- when an important decision is made, propose recording it — and which skill
  owns the record.

## 2. The canonical block

Append to root `CLAUDE.md`, adapting only the paths (section 4):

```markdown
## Keeping context and decisions current

- When the project's structure, conventions, commands or tooling change in a way
  this file or `.claude/rules/` should reflect, update the affected file in the
  same change. With the `tsh-core` plugin installed, invoke
  `/tsh-core:managing-claude-context`; without it, revise by hand and keep this
  file under 200 lines.
- When an important technical decision is made — architecture, technology,
  approach — propose recording it before the work moves on. With the `tsh-core`
  plugin installed, invoke `/tsh-core:managing-decision-records`; without it,
  match the format of the existing records and update the index in
  `docs/decisions/README.md` in the same change.
```

Every path stays in backticks. Written bare with a leading `@`, a path becomes
an import and loads the file at launch — the rule and its rationale are owned by
`managing-claude-context`; this template exists to comply with it.

A third bullet joins the block only where the repository has adopted a domain
dictionary — appended to a repository with none, it is a dead instruction, the same
failure the conditional phrasing below prevents for an uninstalled plugin. Append it
only where `docs/domain-dictionary.md` (or the repository's chosen projection path)
exists:

```markdown
- When code surfaces a term the dictionary doesn't cover, or an existing entry
  looks wrong, record it in the dictionary's inbox in the same change — never
  invent the resolution yourself. With the `tsh-core` plugin installed, invoke
  `/tsh-core:managing-claude-context`; without it, add the entry by hand,
  matching the projection's existing format.
```

## 3. Why the phrasing is conditional

`tsh-core` installs at **user scope** — each teammate individually, not the
repository. The `CLAUDE.md` this block lands in is read by every contributor,
including those who have never installed a plugin. An unconditional
"invoke `/tsh-core:…`" is a dead instruction for them; the conditional form
degrades to a manual procedure that still gets the file updated. Never write the
skill invocation as the only path to the outcome.

The skill names are written out in full precisely because they may be all a
reader without the plugin ever sees: a name like `managing-decision-records`
still says what to do by hand.

## 4. Placement, paths and budget

- The section goes in the **root** `CLAUDE.md`, near the end — after the
  orientation content, alongside any other pointer material. Nested `CLAUDE.md`
  files never repeat it; they concatenate with the root, so it already reaches
  them.
- Adapt the decision-archive path to the repository's real one. A repo keeping
  records in `docs/adr/` gets `docs/adr/README.md` in the second bullet — the
  location convention wins, per `managing-decision-records`.
- The block counts against the root file's 200-line budget. If adding it tips
  the file over, the fix is trimming elsewhere per `managing-claude-context`,
  never dropping the section.

## 5. Repairing a stale variant

A repository that ran init before, or wrote something similar by hand, may
already carry a version of this section. Treat it like any existing `CLAUDE.md`
content:

- **Revise in place, never replace the section wholesale.** Keep lines the team
  added around the two bullets; they are team intent.
- Bring the two bullets up to the canonical wording where they drifted —
  unconditional invocations, renamed skills, a bare `@` path — and report each
  correction.
- If the decision bullet names an archive path that no longer matches the
  repository, fix the path, not the repository's convention.
- Two copies of the section (root and nested, or duplicated in the root) reduce
  to one, in the root.

## 6. What this file does not own

- The **decision-index pointer** — the sentence telling readers to consult
  `docs/decisions/README.md` before changing what a record governs, and that
  only `Accepted` records bind — is owned by `managing-claude-context` and
  written by its Step 5. This section complements that pointer and must not
  duplicate or replace it.
- The record format, numbering and statuses named in the second bullet belong to
  `managing-decision-records`.
- The 200-line budget, the backtick-not-import rule and everything else about
  `CLAUDE.md` content belong to `managing-claude-context`. When this template
  and that skill disagree, that skill wins and this file gets fixed.
