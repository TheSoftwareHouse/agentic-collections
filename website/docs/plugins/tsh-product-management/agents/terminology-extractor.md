---
title: Terminology Extractor
sidebar_label: terminology-extractor
sidebar_position: 7
description: Read-only worker agent that extracts domain-term candidates from supplied material and sweeps a codebase's identifiers for Reconcile mode.
sources:
  - plugins/tsh-product-management/agents/terminology-extractor.md
  - plugins/tsh-product-management/skills/managing-domain-dictionaries/SKILL.md
  - plugins/tsh-product-management/skills/managing-domain-dictionaries/references/reconciling-with-code.md
  - plugins/tsh-product-management/skills/managing-domain-dictionaries/references/review-passes.md
sources_hash: "4ba12e4cae82d467b5a1410140cdde83de151b8bc5fca4b947bca21e5afa31a6"
---

# Terminology Extractor

**Plugin:** `tsh-product-management`  
**Mention:** `@tsh-product-management:terminology-extractor`  
**Model:** `sonnet`  
**Tools:** `Read, Grep, Glob`  
**Preloaded skill:** none. The agent file declares no `skills:` list and is written as a worker for [`managing-domain-dictionaries`](/docs/plugins/tsh-product-management/skills/managing-domain-dictionaries).

Does two reading jobs and nothing else: it extracts term candidates and source-language surface forms from supplied material, and sweeps the identifiers a codebase actually uses when delegated for Reconcile mode. It writes nothing and asks nobody: every write to the dictionary file and every question to the client stays with the skill and the person it is working with.

## Responsibilities

| Area | Coverage |
| :-- | :-- |
| **Inputs** | The delegation must name the material it owns (transcripts, PDFs, designs, backlog context or a codebase path) and which reading job it asks for: term extraction, an identifier sweep, or both. If it names neither, the agent stops and reports that. PDFs are read with `Read`, with an explicit `pages` range beyond 10 pages and chunks of at most 20 |
| **Term extraction** | Collects every candidate noun phrase and its source-language surface forms, attributed to where each was seen. In inflected languages every form of the same word resolves to one lemma before it becomes a candidate row |
| **Homonym candidates** | Two words that look identical but plausibly mean different things in different parts of the product are flagged, not resolved. The `Context` column that would disambiguate is the skill's call |
| **Architecture-word collisions** | A word that collides with an architecture term already in use in the codebase, such as `Service`, `Component`, `Entity`, `Repository`, `Module` or `Controller`, is flagged separately and no side is silently picked |
| **Operations** | Verbs describing something the business does are `Operation` candidates, naming the object acted on and the state transition where the material states one |
| **No invented definitions** | A candidate it cannot ground in the text is reported with `Status` `Inferred` and where it was seen, never asserted as `Agreed` or `Proposed` |
| **Identifier sweep** | In Reconcile mode it reads class names, DTO fields, route segments, enum members and column names with `Grep` and `Glob` across the delegated path, and reports them as found, in their original casing and form. It does not normalize them or match them against dictionary rows, and it does not read or write the dictionary file |
| **Boundaries** | No write tools and no interactive tool. It never speaks to the user directly and does not assign a final `Kind`, `Context` or canonical spelling: it reports candidates, not conclusions |

## What it returns

Its final message is the return value, with no preamble, using the term-table column order from the skill's `dictionary-format.md` (Canonical term, Source term(s), Context, Kind, Definition, UI label(s), Status):

- Term Candidates, one row per candidate
- Homonym Candidates
- Architecture-Word Collisions
- Swept Identifiers, Reconcile mode only: identifier, kind and file path
- Unresolved / Blockers, or "none"

## Used by

[`managing-domain-dictionaries`](/docs/plugins/tsh-product-management/skills/managing-domain-dictionaries) delegates the Harvest reading pass and the Reconcile identifier sweep to it. Its `reconciling-with-code.md` and `review-passes.md` references also name it, for the sweep and for the Undefined review pass.

## Source

[`plugins/tsh-product-management/agents/terminology-extractor.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-product-management/agents/terminology-extractor.md)
