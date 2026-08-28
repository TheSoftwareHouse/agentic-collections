---
name: managing-domain-dictionaries
description: "Produces, reviews and maintains a per-product domain dictionary — canonical business terms, their source-language surface forms, and where a UI label differs from the identifier — through Harvest, Reconcile and Interview modes, checked by eleven review passes and reconciled against a live codebase without ever editing it."
when_to_use: "Trigger on: 'build a glossary', 'what do they call this', ubiquitous language, standardizing terminology across a project, reconciling business terms with code identifiers, or a session started with `/tsh-product-management:domain-dictionary`."
---

# Managing Domain Dictionaries

This is not domain-driven design. A domain dictionary records the vocabulary
the business already uses — canonical terms, their source-language surface
forms, and where the interface says something different from the identifier.
It carries no architectural conclusions: no aggregates, no context maps, no
event storming. A `Context` field disambiguates a homonym; it is not a
bounded-context map.

## Applicability and Precedence

The client's own words outrank inference. An `Agreed` term outranks a
`Proposed` or `Inferred` one on any conflict. On a live project the code is
evidence of drift, never authority — Reconcile mode reports mismatches; it
never lets the codebase overrule an agreed term.

## Non-negotiable Rules

| Severity | Rule |
| --- | --- |
| MUST | Record every gate approval in `.dictionary-gates.md` **before** taking the action it unlocks |
| MUST | Deprecate a term with a successor pointer (`Deprecated → <term>`) — never delete a row |
| MUST | Keep every user-facing question and persistent write in this conversation; `terminology-extractor` writes nothing and asks nobody |
| MUST | Record every rejected candidate and the reason for rejection — part of the record, not discarded |
| NEVER | Mint a canonical term anywhere outside this skill |
| NEVER | Edit code, or present a proposed rename as a fait accompli — Reconcile mode only ever proposes |
| NEVER | Machine-translate a client term without confirming it with the client |
| NEVER | Record a client secret or personal data in a dictionary |

## Reference Loading

| Reference | Load when |
| --- | --- |
| [Dictionary format](./references/dictionary-format.md) | Before creating or editing any dictionary file — the field set, the `Kind` and `Status` vocabulary |
| [Elicitation protocol](./references/elicitation-protocol.md) | Running Interview mode, and for the batching and stop-rule contract on a live project |
| [Review passes](./references/review-passes.md) | Before the review gate — the eleven checks and the confidence defaults |
| [Reconciling with code](./references/reconciling-with-code.md) | Running Reconcile mode against a codebase |
| [Handoff and portability](./references/handoff-and-portability.md) | Closing a session — the provenance header and the handoff menu |

## Modes

Three, composed in a fixed order on a live project: **Harvest → Reconcile →
Interview** for the residue. Pick the entry point from what is on disk:

- Nothing on disk → skip straight to **Interview**.
- Transcripts, PDFs, designs or an existing backlog → **Harvest** term
  candidates first, delegated to `@tsh-product-management:terminology-extractor`.
- A codebase path to check against → **Reconcile**, delegated to the same
  read-only agent for the identifier sweep.

Each mode narrows what Interview still has to ask. Run the eleven review
passes on the result, gate the findings, then close with the handoff.

## Artifacts and Gates

| Artifact | Path | Scope |
| --- | --- | --- |
| Source of truth | `specifications/projects/<project-name>/domain-dictionary.md` | Project, outlives the session |
| Gate ledger | `specifications/projects/<project-name>/.dictionary-gates.md` | Project |
| Session proposal | `specifications/<workshop-name>/.dictionary-delta.md` | Session; merged into the source of truth only after approval |
| Consuming-repo projection | `docs/domain-dictionary.md` (default) | The adopting repository |

The ledger is `.dictionary-gates.md`, never `.gates.md` — the Jira guard
collects `.gates.md` by exact basename, so a distinct filename keeps a
dictionary session from ever arming it.

Three gates, letter-prefixed so none collides with the business-analysis
workflow's numbered gates:

| Gate | Unlocks |
| --- | --- |
| `D1` | Merging `.dictionary-delta.md`'s proposed terms into `domain-dictionary.md` |
| `D2` | Applying accepted review-pass findings to the term table |
| `D3` | Recording a Reconcile-mode disposition — especially a proposed rename — in the dictionary |

Record the approval in `.dictionary-gates.md` before the action it unlocks;
nothing else counts.

## Lifecycle

Status vocabulary and superseding semantics reuse
`/tsh-core:managing-decision-records` rather than inventing a parallel
lifecycle — deprecate, never delete, always with a successor pointer. A term
rename on a live project is an ADR candidate in the consuming repository.

The unresolved-terms inbox is a **return channel, not a write path**: a
consuming repository captures terms discovered during implementation in a
section of its own projection, and the next product-management session drains
it. No session mints a canonical term outside this skill.

## Closing Handoff

Present the handoff menu from `handoff-and-portability.md` — commit, publish
to Confluence, or hand the file over directly, naming none as default — then
point at `/tsh-core:managing-claude-context` for repository adoption, by name
only. That skill is source-agnostic: it wires up whatever dictionary file is
present, however it arrived.
