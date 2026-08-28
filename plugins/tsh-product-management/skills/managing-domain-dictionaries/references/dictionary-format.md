# Dictionary format

A domain dictionary is one Markdown file per product:
`specifications/projects/<project-name>/domain-dictionary.md`. This reference
defines every section it contains, in the order they appear. Every other
`managing-domain-dictionaries` reference, the skill itself, and the
`tsh-core` adoption side cite the field and value names pinned here verbatim —
do not respell them.

This is not domain-driven design. The file records the language the business
already uses. It carries no aggregates, no context maps, no architectural
conclusions. A `Context` field (below) is not a bounded-context map.

## Header — language policy

Every dictionary opens with the policy the rest of the file assumes, so no
agent guesses a project-level decision line by line:

| Field | Content |
| --- | --- |
| Canonical identifier language | Default English |
| Source language(s) | Every language heard in workshops, including mixed forms |
| UI locale(s) | Every locale the product ships in |
| Transliteration rule | How diacritics become identifiers — `ł ą ę ó` and their kin cannot appear in code |
| Do-not-translate list | A pointer to the do-not-translate list below, not a restatement |
| Provenance | Source project, version, date, and what it was last reconciled against |

Provenance is what makes a copy that has travelled into a repository diffable
against its source with no link home — see
[`handoff-and-portability.md`](./handoff-and-portability.md).

## The term table

One row per term, alphabetical by canonical term, so `grep -i kontrahent`
finds it. Seven columns, in this exact order:

| Canonical term | Source term(s) | Context | Kind | Definition | UI label(s) | Status |
| --- | --- | --- | --- | --- | --- | --- |

- **Canonical term** — a singular noun phrase, no abbreviation, in the
  header's canonical language. It is the atom, not a rendering: casing
  belongs to the consuming repository's own convention, not to this file.
- **Source term(s)** — the client's word, plus every observed surface form.
  Inflected languages matter here: `użytkownika / użytkownikowi /
  użytkownicy` must all resolve to one lemma, or neither extraction nor
  search finds them.
- **Context** — which part of the product the term belongs to. Empty (`—`)
  means product-wide. This is the field that lets a deliberate homonym exist:
  Order in Sales and Order in Fulfilment get separate rows, disambiguated by
  Context, rather than one row forcing a single false definition (the
  split-homonyms rule).
- **Kind** — exactly one of: `Actor`, `Entity`, `State`, `Event`,
  `Operation`, `Document`, `Metric`, `Unit`, `Acronym`.
- **Definition** — one line, business language, never an implementation
  detail. "An Order is a row in `orders`" is a defect in this column.
- **UI label(s)** — per locale, and separate from the canonical term. Code is
  English; the interface may not be. An E2E test asserts on the label, an
  engineer names by the identifier, and one column cannot serve both — that
  is why the table carries two, not one.
- **Status** — exactly one of: `Agreed` (confirmed with the client),
  `Proposed`, `Inferred`, or `Deprecated → <successor>`.

## Banned terms

A deny-list, word → replacement, with a one-line reason:

| Banned | Use instead | Reason |
| --- | --- | --- |
| `user` | `Kontrahent` | They are business partners, not application users |

This is the highest-value section per line in the whole file: short,
mechanically checkable, cheap to keep loaded, and it is what actually changes
an agent's output. Treat it as a first-class section, never a footnote. Every
losing candidate from a collapsed synonym (the collapse-synonyms rule) belongs here, not just in
the change log.

## Do-not-translate

Proper nouns, legal instruments and regulated document types have no
equivalent a client would recognise. Forcing a translation invents a word
nobody uses and breaks the demo. A marked entry keeps the source term as
canonical, transliterated for code (`nipNumber`, `jpkReport`):

| Term | Why | Code identifier |
| --- | --- | --- |
| `NIP` | Polish tax identification number; no English equivalent a client uses | `nipNumber` |
| `JPK` | Standard Audit File for Tax; a regulator-defined export format | `jpkReport` |

## Contested terms — including what was rejected

One word maps to several plausible canonical candidates, and whichever wins
propagates into hundreds of identifiers. **The rejected candidates and the
reason for rejection are part of the record.** Without them, every later
session re-litigates the same choice and the vocabulary drifts.

This section also holds architecture-word collisions (the architecture-word-collision rule) — a domain word
that collides with `Service`, `Component`, `Entity`, `Repository`, `Module`
or `Controller`:

| Term | Accepted | Rejected candidates | Reason |
| --- | --- | --- | --- |
| `Kontrahent` | `Kontrahent` (untranslated) | `Counterparty` | Implies a financial-instrument counterparty, narrower than the client's usage |
| | | `Trading partner` | Too generic; no single Polish word the client actually uses |

## State sets

Per entity: the full enumeration of states, which are terminal, and which
transitions exist by name. Status values are the most-missed term class in
practice — every project accretes `pending | in_review | archived` invented
by whoever wrote the first migration, and no glossary ever contains them.

| Entity | States | Terminal | Named transitions |
| --- | --- | --- | --- |
| (example) | State A, State B (terminal) | State B | `operation-name`: State A → State B |

## Unresolved terms — the inbox

Terms encountered but not yet decided, with where they were seen. This is
the return channel from delivery and the agenda for the
next session — a **capture point, not a write path**: nothing here becomes
canonical until a product-management session resolves it.

| Term | Seen in | Note |
| --- | --- | --- |
| (example) | `extracted-tasks.md`, story 2.3 | Meaning unconfirmed with the client |

## Change log

Term added, renamed, deprecated, superseded — with the source. **Never
delete a term**: old tickets, commits and code still contain it, and agents
will meet it.

| Date | Change | Source |
| --- | --- | --- |
| (example) | Added `Term` | workshop-2026-01-01 |

## Worked example

A short, complete dictionary for a fictional Polish-language financial-services
product. Twelve terms plus one deprecated entry — enough to exercise every
`Kind` and every `Status` value, none of it derived from a real client.

### Header

| Field | Content |
| --- | --- |
| Canonical identifier language | English |
| Source language(s) | Polish (client workshops), with English technical vocabulary from the existing codebase |
| UI locale(s) | `pl-PL` |
| Transliteration rule | Strip diacritics for identifiers: `ł→l`, `ą→a`, `ę→e`, `ó→o` (`ł`, `ą`, `ę`, `ó` and their kin cannot appear in code) |
| Do-not-translate list | See below |
| Provenance | Source project `acme-fintech`, version 1.3, 2026-08-20. Last reconciled against `acme-billing-service` @ `a1b2c3d` (2026-08-15) |

### Term table

| Canonical term | Source term(s) | Context | Kind | Definition | UI label(s) | Status |
| --- | --- | --- | --- | --- | --- | --- |
| Faktura | faktura / faktury / fakturę / fakturą | Billing | Entity | A commercial document recording goods or services delivered to a Kontrahent and the amount owed | PL: Faktura | Agreed |
| Faktura korygująca | faktura korygująca / korekta faktury | Billing | Document | A document that corrects a previously issued Faktura; see do-not-translate | PL: Faktura korygująca | Agreed |
| Grosz | grosz / groszy | — | Unit | The minor currency unit, 1/100 of a złoty, used in monetary amounts on a Faktura | PL: gr | Agreed |
| JPK | JPK / Jednolity Plik Kontrolny | — | Acronym | The Standard Audit File for Tax, a structured export the tax authority requires | PL: JPK | Agreed |
| Kontrahent | kontrahent / kontrahenta / kontrahentowi / kontrahenci | Sales | Actor | A business partner engaged in a commercial transaction with the company | PL: Kontrahent | Agreed |
| Należność przeterminowana | należność przeterminowana / zaległość | Billing | Metric | The total value of Faktura in the Przeterminowana state at a point in time | PL: Należność przeterminowana | Inferred |
| NIP | NIP / numer NIP | — | Acronym | The Polish tax identification number assigned to a Kontrahent | PL: NIP | Agreed |
| Opłacona | opłacona | Billing | State | Terminal state reached when Rozliczenie matches a payment to a Faktura in full | PL: Opłacona | Agreed |
| Przeterminowana | przeterminowana | Billing | State | State reached when a Faktura's payment due date passes unpaid | PL: Przeterminowana | Agreed |
| Rozliczenie | rozliczenie / rozliczyć / rozliczono | Billing | Operation | Matching a payment against one or more Faktura, moving it to the Opłacona state | PL: Rozliczenie | Proposed |
| Wystawienie faktury | wystawienie faktury / wystawić fakturę | Billing | Event | The moment a Faktura is created and enters the Wystawiona state | PL: Wystawienie faktury | Agreed |
| Wystawiona | wystawiona | Billing | State | Initial state of a Faktura once issued, before payment or its due date | PL: Wystawiona | Agreed |
| Zleceniodawca | zleceniodawca | Sales | Actor | Legacy term for the same business partner now called Kontrahent | — | Deprecated → Kontrahent |

### Banned terms

| Banned | Use instead | Reason |
| --- | --- | --- |
| `user` | `Kontrahent` | They are business partners, not application users |
| `client` | `Kontrahent` | Collapsed synonym (the collapse-synonyms rule); also collides with the billing SDK's own `Client` class |

### Do-not-translate

| Term | Why | Code identifier |
| --- | --- | --- |
| `NIP` | Polish tax identification number; no English equivalent a client uses | `nipNumber` |
| `JPK` | Standard Audit File for Tax; a regulator-defined export format | `jpkReport` |
| `Faktura korygująca` | A regulated correction-document type with no client-recognised English name | `correctiveInvoiceId` |

### Contested terms

| Term | Accepted | Rejected candidates | Reason |
| --- | --- | --- | --- |
| `Kontrahent` | `Kontrahent` (untranslated) | `Counterparty` | Implies a financial-instrument counterparty, narrower than the client's usage |
| | | `Trading partner` | Too generic; no single Polish word the client actually uses |
| `Serwis` (architecture collision) | `Portal klienta` | `Serwis` | Client staff use "serwis" for the customer portal, colliding with `Service`, the architecture word already used across the codebase for application services |

### State sets

| Entity | States | Terminal | Named transitions |
| --- | --- | --- | --- |
| Faktura | Wystawiona, Przeterminowana, Opłacona (terminal) | Opłacona | `wystawienie faktury`: (none) → Wystawiona; `upływ terminu płatności`: Wystawiona → Przeterminowana; `rozliczenie`: Wystawiona or Przeterminowana → Opłacona |

### Unresolved terms — the inbox

| Term | Seen in | Note |
| --- | --- | --- |
| Nota księgowa | workshop-2026-08-12 transcript | Not yet defined; possibly a subtype of Document, needs client confirmation |
| Rozrachunek | code identifier `rozrachunekService` | Meaning unclear from the code alone; ask the client before assigning a Kind |

### Change log

| Date | Change | Source |
| --- | --- | --- |
| 2026-06-01 | Added Kontrahent, Faktura, NIP, JPK | workshop-2026-06-01 (Interview) |
| 2026-07-15 | Added Faktura korygująca, marked do-not-translate | Harvest, workshop-2026-07-15 transcript |
| 2026-08-15 | Added Rozliczenie, Wystawienie faktury, state set for Faktura, Grosz, Należność przeterminowana | Reconcile against `acme-billing-service` @ `a1b2c3d` |
| 2026-08-20 | Deprecated Zleceniodawca → Kontrahent | Reconcile session; code identifier `zleceniodawcaId` found unused in the live codebase |
