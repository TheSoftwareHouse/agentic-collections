---
title: Managing Decision Records
sidebar_label: managing-decision-records
sidebar_position: 4
description: Owns the shape and lifecycle of architecture decision records, including the four-section format, status vocabulary, numbering, superseding and index upkeep.
sources:
  - plugins/tsh-core/skills/managing-decision-records/
sources_hash: "b18c7f67752988334dcf26de6a1e2ae4bbef696130c53c58bc49d36dd5319ff2"
---

# Managing Decision Records

**Plugin:** [tsh-core](/docs/plugins/tsh-core/)  
**Invoke:** `/tsh-core:managing-decision-records` (also loaded automatically when a request matches its description)  
**Used by:** [init](/docs/plugins/tsh-core/skills/init) (hands decision candidates to it), [managing-claude-context](/docs/plugins/tsh-core/skills/managing-claude-context) and [writing-technical-documents](/docs/plugins/tsh-core/skills/writing-technical-documents) (each names it as the owner of record format), [writing-project-knowledge](/docs/plugins/tsh-product-management/skills/writing-project-knowledge), [managing-domain-dictionaries](/docs/plugins/tsh-product-management/skills/managing-domain-dictionaries) and [initializing-project-context](/docs/plugins/tsh-product-management/skills/initializing-project-context) (in tsh-product-management), [designing-multi-cloud-architecture](/docs/plugins/tsh-platform-engineering/skills/designing-multi-cloud-architecture) (in tsh-platform-engineering), and [configuring-serverless-service](/docs/plugins/tsh-stack-serverless/skills/configuring-serverless-service) (in tsh-stack-serverless)

Owns what a decision record is: its sections, status, number and row in the index. It does not own the words inside a record; prose craft belongs to [writing-technical-documents](/docs/plugins/tsh-core/skills/writing-technical-documents). A record earns its keep only when someone later asks "why is it like this?" and gets an answer, so a record with no rationale, or one the index does not list, has cost effort and bought nothing.

The repository's existing ADR convention outranks this format: where records already follow a shape (Nygard, MADR, a house template), match it exactly and apply only the lifecycle rules. `docs/decisions/` is the default location, not a requirement.

## Key Areas

| Area | Coverage |
| :-- | :-- |
| **Record format** | A metadata block (`Status`, `Date`, `Tags`, `Supersedes`, `Superseded by`) and four sections in this order: Decision, Context, Alternatives, Consequences. Decision comes first, and its first sentence states the choice in the present tense as settled fact |
| **Alternatives** | One row per option considered, with the single reason it lost. The section is not optional: without it a record cannot stop re-litigation |
| **Consequences** | What becomes easier, what becomes harder, what is foreclosed, and whether reversing the decision is cheap or expensive |
| **Numbering and naming** | `NNNN-kebab-case-title.md`, zero-padded to four digits, never reused and never renumbered. The filename states the decision, not the topic |
| **Status vocabulary** | Five values: `Proposed`, `Accepted`, `Superseded`, `Rejected`, `Deprecated`. Only `Accepted` binds; the others are history |
| **Superseding** | Write the new record, update the old record's metadata only (its body is never touched), update both index rows, and verify the links resolve in both directions |
| **Index upkeep** | The index row is added in the same change as the record. The record is the source of truth for status and tags, and the index is corrected when they disagree |
| **When to write one** | A record is warranted when a choice was made between real alternatives, it is expensive to reverse, someone will ask why, and the rationale is recoverable now. Conventions go to `CLAUDE.md` or a path-scoped rule instead |

## How It Works

1. **Confirm it is a decision.** Read the threshold reference before creating a file; most things people want to record are conventions.
2. **Read the neighbours.** Open the index and two existing records, match their shape, and check whether an existing record already covers the ground (if so, this is a supersede).
3. **Gather what is actually known.** The constraint that forced the decision, the options considered, why each lost, and the consequences. Ask when the rationale is not recoverable.
4. **Write the record.** Take the next free number and apply `writing-technical-documents` to the prose within the sections.
5. **Handle superseding, if this replaces something.** The old record keeps its body unchanged and gains a forward pointer; the new one points back.
6. **Update the index and stop at status.** Make path, tags, description and status match the record exactly, then state the status you believe is correct and who should confirm it.

## Rules It Enforces

| Rule | Why |
| :-- | :-- |
| Never set or change a status yourself | Marking a record `Accepted` asserts what a team agreed; the skill proposes a status and names who decides |
| Never edit the body of a record whose status is `Accepted` or later | A changed decision gets a new record and a forward link |
| Never delete a record or its index row | The rejected option is the most valuable thing in the archive |
| Name the gap when a rationale cannot be recovered | A plausible invented rationale will be cited later as if it were true |
| Treat only `Accepted` records as binding when reading decisions | A `Superseded` record is never read without its successor |

## What It Does Not Do

- Make the decision, or choose between the options under discussion.
- Govern prose craft (that is `writing-technical-documents`) or define the index schema and its wiring into `CLAUDE.md` (that is [managing-claude-context](/docs/plugins/tsh-core/skills/managing-claude-context)).
- Invent a rationale, a rejected alternative or a consequence to fill a section.

## Reference Files

| Reference | Load when |
| :-- | :-- |
| `record-format.md` | Writing or restructuring any record |
| `status-lifecycle.md` | Setting a status, superseding, or reconciling the index and a record |
| `when-to-write-one.md` | Unsure whether something warrants a record |

## Related Skills

- [managing-claude-context](/docs/plugins/tsh-core/skills/managing-claude-context): owns the index schema, the binding note and the `CLAUDE.md` pointer.
- [writing-technical-documents](/docs/plugins/tsh-core/skills/writing-technical-documents): owns the prose inside a record.
- [init](/docs/plugins/tsh-core/skills/init): ensures a decision index exists and proposes record candidates without writing them.

## Source

- [`plugins/tsh-core/skills/managing-decision-records/SKILL.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-core/skills/managing-decision-records/SKILL.md)
- [`plugins/tsh-core/skills/managing-decision-records/references/`](https://github.com/TheSoftwareHouse/agentic-collections/tree/main/plugins/tsh-core/skills/managing-decision-records/references)
