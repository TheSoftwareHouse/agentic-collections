---
title: Domain Dictionary
sidebar_label: domain-dictionary
sidebar_position: 3
description: Entry-point command for producing, reviewing and maintaining a per-product domain dictionary, the canonical business-term glossary.
sources:
  - plugins/tsh-product-management/skills/domain-dictionary/
  - plugins/tsh-core/skills/managing-claude-context/references/adopting-a-domain-dictionary.md
  - plugins/tsh-product-management/skills/orchestrating-business-analysis/SKILL.md
  - plugins/tsh-product-management/skills/analyzing-discovery-context/SKILL.md
  - plugins/tsh-product-management/skills/extracting-epics-and-stories/SKILL.md
  - plugins/tsh-product-management/skills/reviewing-backlog-quality/SKILL.md
sources_hash: "746f692e2334ffda7ae72a93ae6d5aff271e7f4e158a5e4e793ef714796019f6"
---

# Domain Dictionary

**Plugin:** `tsh-product-management`  
**Invoke:** `/tsh-product-management:domain-dictionary <target>`. It runs only when you invoke it (`disable-model-invocation: true`).  
**Used by:** [`orchestrating-business-analysis`](/docs/plugins/tsh-product-management/skills/orchestrating-business-analysis), [`analyzing-discovery-context`](/docs/plugins/tsh-product-management/skills/analyzing-discovery-context), [`extracting-epics-and-stories`](/docs/plugins/tsh-product-management/skills/extracting-epics-and-stories) and [`reviewing-backlog-quality`](/docs/plugins/tsh-product-management/skills/reviewing-backlog-quality) point to it, either to suggest running it or to feed it terms. `tsh-core`'s `/tsh-core:managing-claude-context` also names it as the producing side of dictionary adoption.

A command, not a routing surface. It produces the canonical business-term glossary for one product, which is not domain-driven design. If you supply nothing, it asks what to work on before doing anything else: a project name, a workshop directory of transcripts, PDFs or designs, or a repository path to reconcile terms against.

## Key Areas

| Area | Coverage |
| :-- | :-- |
| **What it runs** | It invokes `/tsh-product-management:managing-domain-dictionaries` and follows it end to end. That skill owns the three modes, the elicitation protocol, the review passes and the handoff. The instructions say to invoke the skill rather than read its `SKILL.md` |
| **Mode selection** | Nothing on disk for the project starts Interview. Transcripts, PDFs, designs or an existing backlog start Harvest. A codebase path starts Reconcile. On a live project the modes compose in order: Harvest, then Reconcile, then Interview for whatever is still missing |
| **Prerequisites check** | Figma MCP is needed when Harvest reads design material. Atlassian MCP is needed only if the Confluence option of the handoff menu is chosen; committing into a repository or handing the file over directly need neither |

## What you end up with

- `specifications/projects/<project-name>/domain-dictionary.md`, the source of truth, which outlives the session
- `specifications/projects/<project-name>/.dictionary-gates.md`, the gate ledger (`D1` to `D3`)
- `specifications/<workshop-name>/.dictionary-delta.md`, this session's proposal, merged into the project file only after approval
- `docs/domain-dictionary.md` by default, the projection in the adopting repository, written on the `/tsh-core:managing-claude-context` side of the handoff

## Related skills

- [`managing-domain-dictionaries`](/docs/plugins/tsh-product-management/skills/managing-domain-dictionaries) holds the full procedure and its references.
- [`terminology-extractor`](/docs/plugins/tsh-product-management/agents/terminology-extractor) is the read-only worker behind Harvest and Reconcile.

## Source

[`plugins/tsh-product-management/skills/domain-dictionary/SKILL.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-product-management/skills/domain-dictionary/SKILL.md)
