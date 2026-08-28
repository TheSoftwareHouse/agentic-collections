# Review passes

Eleven passes check the dictionary itself, not the backlog — run once a dictionary
exists, to catch defects a term-by-term reading misses. They reuse
`reviewing-backlog-quality`'s confidence vocabulary (High / Medium / Low) and its
file-first, one-disposition-question gate shape rather than inventing a parallel
one. Column, `Kind` and `Status` names are those pinned in
[`dictionary-format.md`](./dictionary-format.md); this file does not respell them.

## Homonym

Checks whether one canonical term carries two distinct meanings with no `Context`
value separating them — the required split did not happen.

*Example finding*: `Zamówienie` has one row whose Definition blends a Sales-side
"purchase request from a Kontrahent" and a Fulfilment-side "picking and shipment
unit," with `Context` left empty.

Confidence default: **High** — one canonical term, one Definition field, and a
definition visibly serving two audiences is a mechanical read.

## Synonym

Checks whether two rows carry the same Definition — the collapse that should have
merged them into one canonical term plus a Banned terms row for the loser.

*Example finding*: `Klient` and `Kontrahent` are both defined as "a business
partner engaged in a commercial transaction," and neither row names the other as a
rejected candidate.

Confidence default: **High**.

## Orphan

Checks whether a defined term appears nowhere else — no story, document or code
identifier anywhere in the project mentions it — which usually means it was
captured ahead of need, or never was a real term.

*Example finding*: `Kredyt kupiecki` has a row and a Definition, but no
`extracted-tasks.md` story, document, or code identifier in the reconciled
repository contains it.

Confidence default: **Medium** — a term with no observed use is not automatically
wrong; it may be one the client raised once, ahead of the project reaching it.

## Undefined

Checks the inverse of Orphan: a term appearing in `extracted-tasks.md` or in the
code with no row in the table.

This pass is **partly automatable**: sweeping capitalised noun phrases in
`extracted-tasks.md` and code identifiers, then flagging the ones the table does not
cover, is exactly the read-only sweep `@tsh-product-management:terminology-extractor`
performs — it returns candidates and misses, it does not decide which belong in the
table.

*Example finding*: the sweep returns `Rozliczenie` as a code identifier
(`rozliczenieService`) used in four stories, with no matching table row.

Confidence default: **High** — the sweep either finds the identifier or it does
not; there is no partial credit.

## Circularity

Checks whether a Definition defines the term using a form of itself, so a reader
learns nothing new.

*Example finding*: `Broker` — Definition reads "A Broker is someone who brokers."

Confidence default: **High**.

## Implementation leak

Checks whether a Definition describes storage or a framework detail rather than
business meaning — `dictionary-format.md`'s own rule that "An Order is a row in
`orders`" is a defect in that column.

*Example finding*: `Faktura` — Definition reads "A record in the `invoices` table
with a `status` enum," with no business-language sentence anywhere in the row.

Confidence default: **High**.

## Untranslated

Checks whether a source-language term sits in the Canonical term column with no
corresponding Do-not-translate entry and no Contested terms note explaining why it
was kept — an accidental untranslated term, not a deliberate one.

*Example finding*: `Zamówienie` is the Canonical term with no do-not-translate row
and no contested-terms entry, so nothing on the page says whether the Polish
spelling was a decision or an oversight.

Confidence default: **Medium** — a genuine do-not-translate case looks identical
until the surrounding sections are checked.

## State completeness

Checks every state set for a terminal state, and for transitions that name a state
absent from the States column.

*Example finding*: `Faktura`'s state set lists `Wystawiona` and `Przeterminowana`
with no state marked terminal, and a `rozliczenie` transition targets `Rozliczona`,
a state that does not appear in States.

Confidence default: **High**.

## Architecture collision

Checks for a domain term that collides with `Service`, `Component`, `Entity`,
`Repository`, `Module` or `Controller` with no disambiguation recorded in Contested
terms.

*Example finding*: `Serwis` is used as the canonical term for the customer portal,
colliding with `Service`, the architecture word already in use for application
services across the codebase, and Contested terms carries no row for it.

Confidence default: **High**.

## Industry mismatch

Checks whether the client's meaning of a term differs from the term's
industry-standard meaning, where the gap is a risk for anyone who assumes the
standard sense — an accounting integration, a regulator, a new hire.

*Example finding*: `Faktura korygująca`'s Definition covers only quantity
corrections, while the industry-standard Credit Note also covers price
corrections — a downstream accounting integration built against the standard
meaning would silently mishandle a price correction.

Confidence default: **Low** — the standard meaning must be verified externally
before the finding is trusted, the same caveat `reviewing-backlog-quality`'s
domain-research pass carries.

## Confidence

Checks for a term with `Status: Inferred` that has already propagated — used
across several stories or code identifiers — where reversing it later is expensive
precisely because it was never confirmed.

*Example finding*: `Rozliczenie` is `Inferred` but already appears as a code
identifier and in four stories; the finding recommends confirming it with the
client before more code depends on the guess.

Confidence default: **High** — `Inferred` plus multiple observed uses is a
mechanical join, not a judgment call.

## Confidence defaults

| Pass | Confidence default | Typical disposition |
| --- | --- | --- |
| Homonym | High | Split into two rows, disambiguated by `Context` |
| Synonym | High | Merge into one canonical term; add the loser to Banned terms |
| Orphan | Medium | Confirm still needed, or move to Unresolved terms |
| Undefined | High | Add a row; source it from the `terminology-extractor` sweep |
| Circularity | High | Rewrite the Definition in business language |
| Implementation leak | High | Rewrite the Definition; drop the storage/framework detail |
| Untranslated | Medium | Add a Do-not-translate row, or translate it |
| State completeness | High | Mark a terminal state, or add the missing state |
| Architecture collision | High | Record a disambiguation in Contested terms |
| Industry mismatch | Low | Confirm with the client; cite the industry source found |
| Confidence | High | Confirm the term with the client; update Status to `Agreed` |

## The gate — one approval, before it lands

Findings from all eleven passes go into one review file, never into a run of
individual questions — the same file-first shape `reviewing-backlog-quality` uses
for its Gate 1.5 disposition. Approval is a gate because a name change after code
already depends on it is expensive to reverse.

- Write every finding to the review file first — canonical term, pass, what it
  checks, proposed correction — before asking anything.
- Ask **one** disposition question against the whole file: which findings are
  accepted, which are rejected, and why for each rejection.
- Record the approval in `.dictionary-gates.md` before applying any accepted
  finding to the dictionary. Nothing changes the term table until this row is
  written.
- Never silently change a canonical term, a `Status`, or a state set — every
  change traces to an accepted finding.
