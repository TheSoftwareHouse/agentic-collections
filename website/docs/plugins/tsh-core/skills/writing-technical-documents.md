---
title: Writing Technical Documents
sidebar_label: writing-technical-documents
sidebar_position: 6
description: Applies TSH's writing standard to any technical document so it leads with the conclusion, states only verified facts and is short enough to be read.
sources:
  - plugins/tsh-core/skills/writing-technical-documents/
sources_hash: "50094350d26cad0966b3931526ad1686f1e7f164274711f9f84859f63a72b147"
---

# Writing Technical Documents

**Plugin:** [tsh-core](/docs/plugins/tsh-core/)  
**Invoke:** `/tsh-core:writing-technical-documents` (also loaded automatically when a request matches its description)  
**Used by:** [managing-decision-records](/docs/plugins/tsh-core/skills/managing-decision-records) and [managing-claude-context](/docs/plugins/tsh-core/skills/managing-claude-context) (both hand prose craft to it), [auditing-accessibility](/docs/plugins/tsh-product-testing/skills/auditing-accessibility), [auditing-aws-cost](/docs/plugins/tsh-stack-aws/skills/auditing-aws-cost), [auditing-azure-cost](/docs/plugins/tsh-stack-azure/skills/auditing-azure-cost), [auditing-gcp-cost](/docs/plugins/tsh-stack-gcp/skills/auditing-gcp-cost) and the [infrastructure-auditor](/docs/plugins/tsh-platform-engineering/agents/infrastructure-auditor) agent (each applies it to a written report)

Produces technical documents people actually read: the conclusion first, every claim verified, and nothing left in that does not earn its place. The craft rules are drawn from *Writing for Busy Readers* by Todd Rogers and Jessica Lasky-Fink, restated as checkable rules.

It governs prose craft, never structure. It does not decide what sections an ADR needs or what a user story must contain. When an artifact already has a required shape (from the repository, the tracker or another TSH skill), that shape wins and this skill governs only the words inside it. A request for a template, a section list or "what should a good X contain" is declined: the skill names the boundary and offers craft help instead, such as tightening a draft or making acceptance criteria checkable.

## Key Areas

| Area | Coverage |
| :-- | :-- |
| **Conclusion first** | The conclusion, decision or required action goes in the first sentence; background comes after, or not at all |
| **Verified facts** | Every path, command, flag, version and link target is checked against the source before it is written. An unconfirmed claim is omitted or marked as an open question |
| **Cutting** | Every word, sentence and section that does not change what the reader thinks or does is cut; filler such as "comprehensive", "robust", "seamless", "leverage", "in order to" and "simply" is banned |
| **Form** | One idea per paragraph; a table or list when content is enumerable, prose when it is not; headings that summarise what follows; the reader's next action at the end whenever one exists |
| **Domain terms** | Where the project has a domain dictionary, its canonical terms are used, never an invented synonym or translation |
| **Revision pass** | Mandatory before handoff: a first draft is never the deliverable |

## How It Works

1. **Name the artifact and the reader.** State the document type, who reads it and what decision they make afterwards. If the decision cannot be named, the document has no job.
2. **Load the matching reference** before writing the first sentence.
3. **Gather and verify the facts** from code, configuration and neighbouring documents.
4. **Draft conclusion-first,** with short sentences, one idea per paragraph and active voice.
5. **Run the revision pass** and apply it to the draft.
6. **Verify links and paths.** Confirm every internal link resolves and every referenced path exists; for documentation-site changes, run the site build.

## Reference Files

| Reference | Load when | Covers |
| :-- | :-- | :-- |
| `revision-pass.md` | A draft exists and is being tightened, shortened or clarified | The mechanical cut list: dead openings, filler phrases, marketing adjectives, hedges, buried conclusions |
| `repository-documentation.md` | Writing a README, `/docs` page, runbook or documentation-site page | The reader who arrives with no context, the exists/use/next contract, command verification, runbook shape |
| `change-records.md` | Writing a CHANGELOG entry, PR description, release note or migration guide | Leading with impact and required action, naming who is affected, describing breakage in the reader's terms |
| `decision-records.md` | Writing an ADR, RFC or technical proposal | Decision before deliberation, one-line alternatives, concrete consequences and reversibility |
| `work-items.md` | Writing a ticket, user story, acceptance criteria or bug report | The reader deciding whether to pick it up, cutting origin narrative, checkable "done", observed versus expected |

## What It Does Not Do

- Define, propose or produce the structure, template or required sections of any artifact, even when asked directly.
- Govern commit subject lines or pull request titles; the repository's own commit convention owns those.
- Rewrite historical CHANGELOG entries, decision records or incident reports.
- Invent facts, examples or rationale to fill an empty section, or approve technical accuracy the source files do not show.

## Related Skills

- [managing-decision-records](/docs/plugins/tsh-core/skills/managing-decision-records): owns the section set, metadata and status vocabulary of a decision record; this skill never overrides it.
- [managing-claude-context](/docs/plugins/tsh-core/skills/managing-claude-context): owns the index schema and wiring for decision records.

## Source

- [`plugins/tsh-core/skills/writing-technical-documents/SKILL.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-core/skills/writing-technical-documents/SKILL.md)
- [`plugins/tsh-core/skills/writing-technical-documents/references/`](https://github.com/TheSoftwareHouse/agentic-collections/tree/main/plugins/tsh-core/skills/writing-technical-documents/references)
