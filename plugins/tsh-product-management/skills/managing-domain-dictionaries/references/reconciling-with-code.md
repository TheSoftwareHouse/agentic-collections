# Reconciling with code

Reconcile mode diffs the vocabulary a codebase actually uses against the business
terms in [`dictionary-format.md`](./dictionary-format.md) — the term table's
`Canonical term`, `Source term(s)` and `Status` columns, unchanged — and produces a
drift report with a disposition per mismatch. Input is an existing codebase plus a
dictionary or a set of business terms; output is that drift report, never a code
change.

## The sweep

The sweep reads the identifiers actually present in the code — class names, DTO
fields, route segments, enum members, column names — and is delegated to
`@tsh-product-management:terminology-extractor`, which is **read-only**: it reads
source files and reports identifiers, it does not write to the codebase and it does
not touch the dictionary file. The skill diffs the swept identifiers against the
term table itself.

A mismatch is any pair where a code identifier and a business term plausibly name the
same thing but the strings disagree — `orderStatus` in code against `Zamówienie` in
the table, or a code identifier with no row in the table at all. Every mismatch gets
exactly one of the three dispositions below; there is no fourth outcome and no
partial credit.

## The three dispositions — always exactly three

For each mismatch, offer all three. The order below is fixed — it runs from most
correct and most expensive to cheapest and least disruptive — and the skill never
picks on the user's behalf.

### 1. Rename the code

Propose that the code identifier change to match the canonical term. This is the
technically correct outcome: the artifact and the codebase agree, and every future
reader meets one name. It is also the most expensive — a rename touches every call
site, every migration that references a column, every test that asserts on a field
name — so it is **only ever proposed**, written into the drift report as a
recommendation with its blast radius, never carried out.

### 2. Accept the code term as canonical

The dictionary changes instead of the code. The code identifier becomes the
`Canonical term`, and the business term that was displaced moves to `Source term(s)`
or, if it is still meaningfully different, to a new row of its own. This is correct
when the code term is already the name every engineer on the project actually says
out loud — the dictionary was behind reality, not the code.

### 3. Record as a legacy alias

Both names live. The code identifier's business-facing counterpart is written into
the term table with `Status` set to `Deprecated → <canonical>`, using the exact
status vocabulary `dictionary-format.md` pins. Nothing moves today: the code keeps
its current identifier, the dictionary keeps the canonical term, and the row records
that the two are the same thing under different names at different points in the
system's history.

## Why option 3 exists

A dictionary that can only demand renames is ignored on the day it lands. Most
mismatches surface in code that is already shipped, already tested and already
load-bearing — insisting on a rename before the dictionary can be trusted turns every
reconcile session into a renegotiation of the backlog. The legacy-alias disposition
lets the dictionary stay accurate about what the code currently says, while still
recording the canonical term for everything written from this point forward. It is
the disposition that makes adoption cheap enough to actually happen.

## The hard boundary

**The skill never edits code, ever.** Reconcile mode is read-only against the
codebase in both directions: the sweep reads identifiers, the skill writes findings
to the drift report and, on disposition 2 or 3, to the dictionary file — never to a
source file, a migration, or a test. A disposition of 2 or 3 is recorded as `D3` in
`.dictionary-gates.md` before it is applied to the dictionary; nothing changes the
term table until that row is written. A proposed rename is written up with its file
list and blast radius so a human or a separate implementation task can act on it; the
skill does not open a pull request, does not run a codemod, and does not present a
rename as a fait accompli that has already happened.

## The drift-report shape

One row per mismatch. Four fields, in this order:

| Code identifier | Business term | Disposition | Rationale |
| --- | --- | --- | --- |
| `orderStatus` | Zamówienie | Accept code term as canonical | Every engineer and every recent commit already say "order"; the Polish term was workshop-only and never reached the codebase |
| `zleceniodawcaId` | Kontrahent | Legacy alias — `Deprecated → Kontrahent` | Column is live in production; renaming it means a migration plus every downstream report, out of scope for this session |
| `custStatus` | Status Kontrahenta | Rename the code (proposed) | Abbreviation with no business reader; low blast radius — one service, three call sites |

- **Code identifier** — the identifier as swept from the codebase, in backticks,
  exactly as it appears in source.
- **Business term** — the matching `Canonical term` from the dictionary, or the
  closest business-language candidate if no row exists yet.
- **Disposition** — exactly one of the three above, named the same way every time so
  the report is greppable across sessions.
- **Rationale** — one line: why this mismatch got this disposition and not one of
  the other two. For disposition 1, the rationale doubles as the blast-radius note
  the eventual rename task will need.

The drift report is written to disk alongside the dictionary, not held only in the
conversation — a reconcile session against a large codebase produces more mismatches
than fit in one sitting, and the report is what the next session resumes from.
