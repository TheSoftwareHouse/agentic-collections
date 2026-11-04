---
title: Managing Domain Dictionaries
sidebar_label: managing-domain-dictionaries
sidebar_position: 11
description: Produces, reviews and maintains a per-product domain dictionary through Harvest, Reconcile and Interview modes, checked by eleven review passes.
sources:
  - plugins/tsh-product-management/skills/managing-domain-dictionaries/
  - plugins/tsh-product-management/skills/domain-dictionary/SKILL.md
sources_hash: "ff7e038b76fad4c1cde2f234a532044f40588d0cc7771cd60b63b53ad830cb6e"
---

# Managing Domain Dictionaries

**Plugin:** `tsh-product-management`  
**Invoke:** `/tsh-product-management:managing-domain-dictionaries`. Claude also loads it when a request matches its description. The [`domain-dictionary`](/docs/plugins/tsh-product-management/skills/domain-dictionary) command invokes it.  
**Used by:** [`domain-dictionary`](/docs/plugins/tsh-product-management/skills/domain-dictionary). The skill delegates its reading passes to the [`terminology-extractor`](/docs/plugins/tsh-product-management/agents/terminology-extractor) agent.

A domain dictionary records the vocabulary the business already uses: canonical business terms, their source-language surface forms, and where the interface says something different from the identifier. It is not domain-driven design and carries no architectural conclusions: no aggregates, no context maps, no event storming. A `Context` field disambiguates a homonym and is not a bounded-context map.

## Key Areas

| Area | Coverage |
| :-- | :-- |
| **Precedence** | The client's own words outrank inference. An `Agreed` term outranks a `Proposed` or `Inferred` one. On a live project the code is evidence of drift, never authority |
| **Term table** | One row per term, alphabetical by canonical term, with seven columns: Canonical term, Source term(s), Context, Kind, Definition, UI label(s), Status. `Kind` is one of `Actor`, `Entity`, `State`, `Event`, `Operation`, `Document`, `Metric`, `Unit`, `Acronym`. `Status` is `Agreed`, `Proposed`, `Inferred` or `Deprecated → <successor>` |
| **Other sections** | A language-policy header with a Provenance field, Banned terms, Do-not-translate, Contested terms including rejected candidates and the reason, State sets, the Unresolved terms inbox and a Change log |
| **Deprecation** | A term is deprecated with a successor pointer and never deleted. Rejected candidates and the reason are recorded |
| **Gates** | Three gates, letter-prefixed so none collides with the business-analysis numbered gates: `D1` merges proposed terms into the dictionary, `D2` applies accepted review-pass findings, `D3` records a Reconcile-mode disposition. Each is recorded in `.dictionary-gates.md` before the action it unlocks. The ledger name differs from `.gates.md` so a dictionary session never arms the Jira guard |
| **Unresolved-terms inbox** | A return channel, not a write path. A consuming repository captures terms discovered during implementation, and the next product-management session drains it |
| **Lifecycle** | Status vocabulary and superseding semantics reuse `/tsh-core:managing-decision-records`. A term rename on a live project is an ADR candidate in the consuming repository |
| **Hard limits** | Never edit code or present a proposed rename as done. Never machine-translate a client term without confirming it with the client. Never record a client secret or personal data. Never mint a canonical term outside this skill |

## Modes

Three modes, composed in a fixed order on a live project: Harvest, then Reconcile, then Interview for the residue.

| Mode | Starts when | What it does |
| :-- | :-- | :-- |
| **Harvest** | Transcripts, PDFs, designs or an existing backlog are supplied | Collects term candidates and source-language surface forms, delegated to [`terminology-extractor`](/docs/plugins/tsh-product-management/agents/terminology-extractor) |
| **Reconcile** | A codebase path is supplied | The same read-only agent sweeps the identifiers the code actually uses. The skill diffs them against the term table and writes a drift report, never a code change |
| **Interview** | Nothing is on disk, or for whatever Harvest and Reconcile left open | Asks about the vocabulary the material could not answer, in a bounded, resumable, batched protocol |

### Reconcile dispositions

Every mismatch between a code identifier and a business term gets exactly one of three dispositions, offered in this fixed order and never chosen on the user's behalf:

1. **Rename the code**: proposed only, with its blast radius, never carried out.
2. **Accept the code term as canonical**: the dictionary changes instead of the code.
3. **Record as a legacy alias**: both names live, with the status `Deprecated → <canonical>`.

The drift report has four fields per mismatch (code identifier, business term, disposition, rationale) and is written to disk so the next session can resume from it. A disposition of 2 or 3 is recorded as `D3` before it is applied.

### Interview protocol

- Eleven probe categories, always asked in the same order: actors and roles, things the business counts or files, lifecycle states, events, operations and their inverses, documents exchanged, money terms, time terms, units and quantities, external systems' own vocabulary, and acronyms in daily use.
- Four analyses run live against every answer: split homonyms, collapse synonyms, detect architecture-word collisions (`Service`, `Component`, `Entity`, `Repository`, `Module`, `Controller`) and collect verbs, not only nouns.
- Up to 4 independent questions per `AskUserQuestion` call, never two about the same term, and an approval always gets its own call.
- The interview ends when every `Actor` has at least one `Entity`, every `Entity` has a state set and every state set names a terminal state, or when the user says stop. Coverage is reported per probe category as `Covered`, `Partially covered` or `Skipped`.
- State lives on disk in `specifications/<workshop-name>/.dictionary-delta.md`, which is read first on resume and written after every batch of answers.

### Review passes

Eleven passes check the dictionary itself, not the backlog: Homonym, Synonym, Orphan, Undefined, Circularity, Implementation leak, Untranslated, State completeness, Architecture collision, Industry mismatch and Confidence. Findings go into one review file with one disposition question, and the approval is recorded as `D2` before anything changes the term table.

## Artifacts

| Artifact | Path | Scope |
| :-- | :-- | :-- |
| Source of truth | `specifications/projects/<project-name>/domain-dictionary.md` | Project, outlives the session |
| Gate ledger | `specifications/projects/<project-name>/.dictionary-gates.md` | Project |
| Session proposal | `specifications/<workshop-name>/.dictionary-delta.md` | Session, merged only after approval |
| Consuming-repository projection | `docs/domain-dictionary.md` by default | The adopting repository |

## Closing handoff

A session closes with a menu of three options, none named as the default: commit into the product repositories, publish to Confluence (only when the Atlassian server is connected), or hand the file over directly. The skill then points at `/tsh-core:managing-claude-context` for repository adoption, by name only. The dictionary is self-describing through its Provenance field and depends on nothing in the product-management workspace, so it works dropped into any repository on its own.

## References

| Reference | Load when |
| :-- | :-- |
| `dictionary-format.md` | Before creating or editing any dictionary file |
| `elicitation-protocol.md` | Running Interview mode |
| `review-passes.md` | Before the review gate |
| `reconciling-with-code.md` | Running Reconcile mode against a codebase |
| `handoff-and-portability.md` | Closing a session |

## Related skills

- [`domain-dictionary`](/docs/plugins/tsh-product-management/skills/domain-dictionary) is the command that starts a session.
- [`reviewing-backlog-quality`](/docs/plugins/tsh-product-management/skills/reviewing-backlog-quality) runs Pass K against the dictionary, and the dictionary's review passes reuse its confidence vocabulary.

## Source

[`plugins/tsh-product-management/skills/managing-domain-dictionaries/SKILL.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-product-management/skills/managing-domain-dictionaries/SKILL.md)
