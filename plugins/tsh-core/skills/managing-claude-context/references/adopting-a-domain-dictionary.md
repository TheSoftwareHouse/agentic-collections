# Adopting a domain dictionary

Use this reference when a repository is adopting a domain dictionary — a
per-product glossary of the client's own vocabulary — or already has one. The
dictionary is produced by `/tsh-product-management:domain-dictionary`, but nothing
here depends on that plugin being installed: this side's job is to wire up whatever
dictionary file is present, however it arrived.

## 1. Why the obvious placement is wrong

The obvious move is to drop the dictionary straight into a path-scoped rule and let
`.claude/rules/` load it wherever it applies. That fails on timing, not content.

Naming happens at **creation** time — the moment someone writes `kontrahent.status`
instead of `counterparty.status`. [`choosing-the-layer.md`](./choosing-the-layer.md)
§4 establishes that a path-scoped rule fires when Claude **reads** a matching
file, not when Claude writes one: "the convention is honoured on edits and ignored
on creation." A dictionary rule scoped to `src/**/*.ts` loads *after* the
badly-named file already exists, which is exactly the moment it was supposed to
prevent.

Combined with the 200-line `CLAUDE.md` budget, that timing gap forces a two-tier
shape: a thin slice that is always loaded, so naming decisions see it before the
first line is typed, and the full artifact reachable on demand for anyone who needs
the definition rather than the reminder.

## 2. The two-tier projection

| Tier | Where | Loads | Content |
| --- | --- | --- | --- |
| Always loaded | Root `CLAUDE.md`, **~15 lines** | Every session, in full | The canonical-language rule, the handful of banned substitutions that matter most, and a backticked pointer to the full dictionary with the instruction to read it before naming anything new |
| On demand | `docs/domain-dictionary.md` (default) | When Claude reads it | The full artifact — term table, banned terms, contested terms, state sets, the inbox, the change log |
| Edit time | `.claude/rules/*.md` with `paths:` over source globs | When Claude reads a matching source file | The naming constraint, **pointing at** the dictionary rather than restating it |

This is not a new pattern invented for dictionaries. It is the pairing
`choosing-the-layer.md` §5 "They pair, without duplicating" already prescribes for
any guidance needed at both creation and edit time: the skill-or-root layer holds
the thing to check before writing, the rule holds the constraint that fires while
editing, and exactly one copy of the content exists. A dictionary is a worked
instance of that rule, not an exception to it.

The vocabulary block is deliberately small. Fifteen lines buys the rule and the
pointer, not the artifact — see
[`writing-claude-md.md`](./writing-claude-md.md) for what belongs in it and what
does not.

## 3. The backtick rule

State this as hard as the decision-index rule already in
[`SKILL.md`](../SKILL.md): the pointer to `docs/domain-dictionary.md` is written in
backticks, never as a bare `@` import.

```markdown
Canonical terms are pinned in `docs/domain-dictionary.md`. Read it before naming
anything new — do not translate or invent a synonym for a term it defines.
```

A bare `@docs/domain-dictionary.md` is forbidden, not discouraged. Import parsing
expands it at launch, in full, every session — the whole term table, every
contested term and every change-log entry, whether or not the task touches naming
at all. The backticked form is a code span; import parsing skips code spans, so
Claude reads the file on demand instead. Exactly one copy of the dictionary's
content exists, in `docs/domain-dictionary.md`; the root block is a pointer to it,
never a second copy.

The same rule applies inside the edit-time `.claude/rules/*.md` file: it points at
`docs/domain-dictionary.md` in backticks and states the constraint, and does not
paste the term table into the rule body.

## 4. Monorepo slicing

Where bounded contexts differ per package — `packages/billing` calls it an
`Invoice`, `packages/support` calls the same concept a `Case` — the per-context
slice belongs in that package's nested `CLAUDE.md`, not in a second root-level
dictionary.

The decision is not specific to dictionaries: use the ownership test in
[`monorepos-and-scale.md`](./monorepos-and-scale.md) §2. A vocabulary slice one
team's package owns is a nested `CLAUDE.md` beside their code; a naming constraint
that follows a file type across the whole tree stays a central rule. Do not invent
a second predicate for vocabulary — the existing one already decides it.

## 5. The inbox is a capture point, not a write path

A consuming repository will discover terms the dictionary does not cover —
engineering meets vocabulary gaps mid-implementation, and a read-only projection
with no return path guarantees the projection goes stale.

The fix is a section in the repository's own `docs/domain-dictionary.md`
projection — an inbox — where an unresolved term is recorded with where it was
seen. That section is **capture, not resolution**: no session in this repository
mints a canonical term there, proposes a translation, or edits the term table
directly. The next `/tsh-product-management:domain-dictionary` session drains the
inbox and decides. Treat an unresolved term the way the dictionary's own inbox
treats it — an item on the next session's agenda, not a term this repository gets
to settle unilaterally.

## 6. Adopting a file of unknown provenance

A dictionary handed over directly, or found already committed, may or may not carry
the provenance header the producing side writes: source project, version, date, and
what it was last reconciled against.

- **Header present** — record it in the projection as-is. It is what makes the
  copy diffable against its origin later.
- **Header absent** — do not infer one. State plainly in the projection that
  provenance is unknown, rather than implying a source or a reconciliation date the
  file does not claim. A dictionary without a header is still worth adopting; it is
  not worth presenting as more current or more authoritative than it is.

Either way, this skill does not verify that the file matches any other repository
carrying "the same" dictionary — cross-repository reconciliation is out of scope
here, same as it is on the producing side.

## 7. The derivable-fact carve-out

This skill's own rule — **never write a fact Claude can derive from the
codebase** — does not apply to a domain dictionary, and this has to be stated
explicitly or the rule eats the feature.

A dictionary is not derivable. It comes from the client, not from the code: no
amount of reading `src/` recovers that the business calls a `Partner` a `Reseller`
as of month six, or that `kontrahent` was chosen over `counterparty` and why. And on
a live project the dictionary **deliberately contradicts the code** — a `Deprecated
→ <successor>` entry exists precisely because the identifier in the codebase is the
wrong word and the dictionary is what says so. A drift audit that treats
disagreement with the code as staleness and prunes the vocabulary block has broken
the one thing the dictionary exists to hold: the record of what changed and why.
[`auditing-for-drift.md`](./auditing-for-drift.md) carries the matching reminder at
the point an audit would otherwise make that mistake.

## Sources

Producing side, referenced by name only: `/tsh-product-management:domain-dictionary`.
