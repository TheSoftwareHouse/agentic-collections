# Writing the proposal

Read this before writing the file. The document is the entire output of a retro, so its
shape is not cosmetic — it is what decides whether a reader can check the reasoning or
has to take it on faith.

## Location and name

Default: `docs/extension-proposals/<YYYY-MM-DD>-<slug>.md`, in the repository the
session ran in.

**Not `.claude/`.** Claude Code treats that directory as sensitive and refuses writes
into it even under `acceptEdits`, so a retro that targets it fails at the last step with
every candidate already analysed. `docs/` is the default for that reason, not for
tidiness.

- One file per retro. Never append to or overwrite a previous one — each retro is
  evidence from one session, and merging them destroys that.
- `<slug>` names the session's subject in two to four kebab-case words, not the word
  "retro" repeated. `2026-08-24-worktree-skill-authoring.md`, not
  `2026-08-24-retro-2.md`.
- If a file for that date and slug already exists, add a `-2` suffix rather than
  touching it.
- **An existing convention wins.** If the repository already has a proposals directory,
  a tooling backlog, or a documented place for suggestions, file it there and say so in
  the report.

## The header block

Every file opens with the header, before any candidate. It exists so a reader knows
what the retro could and could not see.

```markdown
# Extension proposals — <session subject>

- **Date:** 2026-08-24
- **Session:** <session id, or "current session" if unavailable>
- **Focus:** <the $ARGUMENTS value, or "whole session">
- **Substrate:** in-context conversation | transcript digest | both
- **Not analysed:** <what was outside the focus or lost to compaction, or "nothing">
- **Status:** proposal — nothing in this file has been built

<one paragraph: what the session was doing, so a reader who was not there can judge
the evidence below>
```

When the substrate was a digest, `Session` names the id that was digested rather than
the one you are running in, and `Not analysed` carries the digest's own `Not included`
line. [`analysing-a-prior-session.md`](./analysing-a-prior-session.md) has the table for
every case, including the ones where the tool failed.

The `Not analysed` line is the one people are tempted to leave off. A retro over a
compacted session is still worth writing; a retro that hides that it was partial is
not.

## One section per candidate

Number them `P1`, `P2`, … in descending confidence, so the strongest finding is read
first and a reader can stop early.

```markdown
## P1 — <imperative title: what the artifact would do>

- **Primitive:** skill · **Confidence:** strong
- **Target:** `plugins/<plugin>/skills/<name>/` — marketplace `<repo>`
- **Handoff:** `/tsh-core:authoring-claude-extensions`, after `<repo>`'s own
  contribution and release procedure

**Evidence** — 3 occurrences

1. <quote>, when <where in the session>
2. <quote>, when <where in the session>
3. <quote>, when <where in the session>

**Trigger** — <the concrete moment it fires again>

**What it would absorb** — <what the artifact does instead of the human or Claude>

**Rejected alternative** — <primitive considered> , because <reason>

**Cost if shipped** — <what installers pay: a preloaded description, an agent
definition, a hook firing in every repository — or "repo-local, no shared cost">
```

Rules for the fields:

- **Evidence** is quotes with locations. A summary of what happened is not evidence,
  because it cannot be checked.
- **Trigger** is a moment, not a topic. If it reads like a subject area, it is not
  finished.
- **Rejected alternative** is never "none". If nothing else was plausible, say which
  primitive was the nearest miss and why it loses — that is the useful part.
- **Cost if shipped** is required whenever the target is shared. Omitting it makes the
  proposal read as free.

## Confidence vocabulary

Exactly three values, so the word means the same thing in every retro:

| Value | Means |
| --- | --- |
| `strong` | Three or more occurrences, an unambiguous trigger, and an obvious primitive |
| `tentative` | Meets the two-occurrence floor, but the trigger or the primitive is arguable |
| `speculative` | **Not permitted in a candidate section.** A speculative finding belongs under rejected candidates |

There is no `high`/`medium`/`low` variant and no fourth value. A candidate that does not
fit `strong` or `tentative` is a rejection.

## The rejected-candidates section

Always present, even when empty, and always last:

```markdown
## Rejected candidates

- **<what it was>** — rejected: <reason>
- **<what it was>** — rejected: one occurrence only
- **<what it was>** — rejected: out of requested scope
```

This section is what makes the retro auditable. Without it a reader cannot tell a
thorough analysis that found one thing from a shallow one that noticed one thing.

## When nothing cleared the bar

Write the file anyway. Header, then:

```markdown
## No candidates

This session produced no friction meeting the evidence bar in
`detecting-candidates.md`. <One sentence on why — short session, novel one-off work, no
repetition.>
```

…followed by the rejected-candidates section. A recorded empty retro is evidence that
the session was examined, which is worth having; a retro that invents a finding to
avoid looking empty is worth less than nothing.

## Tone

The document is read by a person deciding whether to spend an afternoon. Lead with the
conclusion, state only what the session actually shows, and cut every sentence that
does not help them decide. Do not editorialise about how the session went — the subject
is the tooling, not the work.
