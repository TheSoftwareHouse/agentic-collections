# Elicitation protocol

The Interview mode's method for asking about the vocabulary the material could not
answer on its own — bounded, resumable, and batched, so a session never turns into
an unstructured chat that a client tires of halfway through. It runs standalone when
nothing is on disk, and it runs again as the last step on a live project, closing
the residue Harvest and Reconcile left open.

## Mode composition

The three modes compose in one fixed order:

| Order | Mode | What it contributes before Interview runs |
| --- | --- | --- |
| 1 | Harvest | Term candidates and source-language surface forms pulled from transcripts, PDFs, designs and an existing backlog |
| 2 | Reconcile | A drift report against the code, each mismatch already dispositioned (see [`reconciling-with-code.md`](./reconciling-with-code.md)) |
| 3 | Interview | Everything Harvest and Reconcile left open — the residue |

A project with nothing on disk skips straight to Interview: there is no material to
harvest and no code to reconcile against. A live project runs all three, in this
order, because each mode narrows what the next one still has to ask.

## The eleven probe categories, in order

Fixed, and asked in this order every time — a wandering order re-asks the same
ground and loses the client's patience before the interview earns its artifact.
Each probe targets one or more `Kind` values from
[`dictionary-format.md`](./dictionary-format.md); use those `Kind` strings verbatim
when recording a candidate row.

| # | Probe category | Typically finds `Kind` | What to ask |
| --- | --- | --- | --- |
| 1 | Actors and roles | `Actor` | Who does things in this product — staff, clients, external parties, systems acting as a party? |
| 2 | Things the business counts or files | `Entity` | What does the business keep a record of, count, or file — one per actor, then product-wide |
| 3 | Lifecycle states of each thing | `State` | For each Entity from probe 2, what states can it be in, and which one is terminal — see [`dictionary-format.md`](./dictionary-format.md#state-sets) |
| 4 | Events | `Event` | "What happens when…" — the moments that move an Entity from one state to another |
| 5 | Operations and their inverses | `Operation` | The verbs staff and clients use, and — deliberately — their inverses: Cancel has a Void, a Refund, a Reverse; ask which the client actually means |
| 6 | Documents exchanged | `Document` | What gets issued, signed, sent or filed — invoices, contracts, confirmations, statements |
| 7 | Money terms | `Metric` or `Unit` | Fee, commission, margin, net/gross, minor currency units — the words that appear on an invoice or a statement |
| 8 | Time terms | `Entity` or `—` | Working day, cut-off, season, grace period — anything with a business meaning narrower than the calendar |
| 9 | Units and quantities | `Unit` | What is counted, in what unit, and whether a unit has a client-specific meaning |
| 10 | External systems' own vocabulary | any | What a payment gateway, a regulator, a partner API or a legacy system calls the same thing |
| 11 | Acronyms in daily use | `Acronym` | What staff say instead of the full term, and whether it needs a do-not-translate entry |

Probe 3 depends on probe 2's answers; probe 5's inverses depend on probe 4's events.
Do not reorder past that dependency, but do not skip a category because an earlier
answer felt complete — a category is closed only by the stop rule below, not by a
hunch.

## The four analyses these probes exist to find

Building a term list is the easy half of this work. Run these checks live, against
every answer, not as a separate pass afterward:

- **Split homonyms** — probes 1, 2 and 6 are where one word turns out to mean
  two things in different parts of the product (Order in Sales versus Order in
  Fulfilment). Ask which part of the product the answer applies to, and record both
  meanings as separate rows disambiguated by `Context` — never collapse them into
  one definition.
- **Collapse synonyms** — when two answers to the same probe describe the
  same thing, ask which word the client actually uses day to day, record the losing
  candidate as a `Source term(s)` entry, and add it to the banned-terms list
  if the team keeps reaching for it in writing.
- **Detect architecture-word collisions** — on every probe, check the
  candidate against `Service`, `Component`, `Entity`, `Repository`, `Module` and
  `Controller`. A collision goes to the contested-terms section with a
  disambiguation, not silently past.
- **Collect verbs, not only nouns** — probe 5 exists specifically for this.
  Every `Operation` candidate must name the object it acts on and the state
  transition it causes; an answer that names only the verb is incomplete until both
  are captured.

## Batching contract

- **Up to 4 independent questions per `AskUserQuestion` call.**
- **Never two questions about the same term in one call** — a later answer can
  invalidate an earlier one asked in the same breath.
- **One question alone for an approval** — a gate decision (the review-pass
  disposition, or closing the interview early) always gets its own call, full
  attention, no batching.
- Order questions by impact within a batch, so a user who stops answering after two
  has still answered the ones that mattered most.
- Exhaust what Harvest and Reconcile already answered before asking — never probe
  for something a transcript, a design file or the codebase already settled.

## Stop rule

The interview for a given scope ends when all three hold:

1. Every `Actor` recorded has at least one `Entity`.
2. Every `Entity` recorded has a state set, even a trivial one.
3. Every state set names a terminal state.

— **or when the user says stop.** A user's explicit stop ends the session
immediately regardless of coverage; the three conditions are the default target,
not a lock the user cannot open early.

**Coverage is reported, not implied.** Before ending, produce a coverage line per
probe category — `Covered`, `Partially covered`, or `Skipped`, with a one-line
reason for anything short of `Covered` — and show it to the user rather than letting
silence stand in for completeness.

## Resumability

A real interview spans several sittings; the conversation itself may be summarized
or lost between them, so it is never the source of truth for what has been asked.

**Asked-and-answered state and probe-coverage state live on disk, in
`specifications/<workshop-name>/.dictionary-delta.md`**, in an Interview State
section shaped like this:

| Probe | Status | Notes |
| --- | --- | --- |
| 1 — Actors and roles | Covered | — |
| 2 — Things counted or filed | Partially covered | Entities for Billing done; Sales actor still open |
| 3 — Lifecycle states | Not started | — |
| … | … | … |

Rules that keep the file authoritative:

- **On resume, read `.dictionary-delta.md` first**, before asking anything. A probe
  marked `Covered` is not re-asked; a term already recorded as answered is not
  re-batched into a new question.
- **Write the status after every batch of answers**, not at the end of the
  session — a session can end at any point, including one the user did not
  announce in advance.
- The same file carries the term candidates this session produced, pending merge
  into the project dictionary — the Interview State table is additional to that
  content, not a replacement for it.
