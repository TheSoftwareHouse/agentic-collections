---
title: Business analysis
sidebar_label: Business analysis
sidebar_position: 5
description: How discovery workshop material becomes Jira-ready epics and stories and a delivery roadmap — five human review gates recorded in a ledger, read-only worker subagents, a hook that blocks Jira writes before Gate 2, and Explore and import entry points.
sources:
  - plugins/tsh-product-management/README.md
  - plugins/tsh-product-management/skills/orchestrating-business-analysis/
  - plugins/tsh-product-management/skills/analyze-materials/SKILL.md
  - plugins/tsh-product-management/skills/explore-materials/SKILL.md
  - plugins/tsh-product-management/skills/domain-dictionary/SKILL.md
  - plugins/tsh-product-management/skills/processing-workshop-transcripts/SKILL.md
  - plugins/tsh-product-management/skills/analyzing-discovery-context/SKILL.md
  - plugins/tsh-product-management/skills/extracting-epics-and-stories/SKILL.md
  - plugins/tsh-product-management/skills/reviewing-backlog-quality/SKILL.md
  - plugins/tsh-product-management/skills/planning-delivery-roadmaps/SKILL.md
  - plugins/tsh-product-management/skills/formatting-jira-issues/
  - plugins/tsh-product-management/skills/managing-domain-dictionaries/SKILL.md
  - plugins/tsh-product-management/agents/
  - plugins/tsh-product-management/hooks/hooks.json
  - plugins/tsh-product-management/hooks/guard-jira-write.mjs
sources_hash: "0c3b724d6a1f3c0de192bb754ae9ff83ae76e9c119e831977ed736c375dc8270"
---

# Business analysis

**Plugin:** [`tsh-product-management`](/docs/plugins/tsh-product-management/) · **Start with:** `/tsh-product-management:analyze-materials <materials>` for the full workflow, or `/tsh-product-management:explore-materials <materials>` to understand the material first. Both take a transcript path, a Figma or FigJam link, a PDF or a folder of documents; `analyze-materials` also takes Jira issue keys or a project key.

The two entry points are commands only (`disable-model-invocation: true`). Each invokes [`orchestrating-business-analysis`](/docs/plugins/tsh-product-management/skills/orchestrating-business-analysis), which owns the procedure, the gates, the delegation and the Jira push. That skill also loads on its own when you ask to "turn this workshop into tickets".

The main conversation is the orchestrator. It owns the materials, the gates, the files and the Jira mutations; the reading and drafting run in read-only worker subagents, so their document parsing stays out of the main context. Output is business-oriented throughout: epics and stories a stakeholder understands without technical knowledge. No technical specifications, architecture decisions, implementation or test plans, and no story-point estimates — sizing guidance only.

## At a glance

<!-- PHASE2(visual): the flow is a plain-text block because @docusaurus/theme-mermaid is not installed — the old site drew this flow as a diagram — decide in Phase 2 whether to add the Mermaid theme or a diagram component -->

```text
materials ─▶ .gates.md ledger
   ─▶ clean the transcript                   (processing-workshop-transcripts)
   ─▶ analyse materials + baseline           (analyzing-discovery-context)
   ─▶ intent brief                 ── Gate 0
   ─▶ epics and stories            ── Gate 1  (extracting-epics-and-stories)
   ─▶ quality review               ── Gate 1.5 (reviewing-backlog-quality)
   ─▶ confirm the updated tasks
   ─▶ roadmap proposal             ── Gate 1.75 Roadmap Review (planning-delivery-roadmaps)
   ─▶ Jira formatting              ── Gate 2  (formatting-jira-issues)
   ─▶ push, read back, archive, refresh the baseline

Explore Mode: analyse ─▶ workshop-context-summary.md ─▶ stop
Import:       Jira keys ─▶ jira-tasks.md (read-only) ─▶ quality review ─▶ …
```

## Who does what

The main conversation runs every skill in the procedure and keeps every user-facing question, persistent write, Jira call and design fetch. Each skill also runs as a worker when the work is delegated:

| Work | Skill | Worker (model) |
| :-- | :-- | :-- |
| Clean and structure a raw transcript | [`processing-workshop-transcripts`](/docs/plugins/tsh-product-management/skills/processing-workshop-transcripts) | [`transcript-cleaner`](/docs/plugins/tsh-product-management/agents/transcript-cleaner) (`haiku`) |
| Synthesise materials, baseline overlap, open questions | [`analyzing-discovery-context`](/docs/plugins/tsh-product-management/skills/analyzing-discovery-context) | [`discovery-analyst`](/docs/plugins/tsh-product-management/agents/discovery-analyst) (`sonnet`) |
| Intent brief, epics, stories | [`extracting-epics-and-stories`](/docs/plugins/tsh-product-management/skills/extracting-epics-and-stories) | [`backlog-extractor`](/docs/plugins/tsh-product-management/agents/backlog-extractor) (`sonnet`) |
| Lite or Full review passes | [`reviewing-backlog-quality`](/docs/plugins/tsh-product-management/skills/reviewing-backlog-quality) | [`backlog-quality-reviewer`](/docs/plugins/tsh-product-management/agents/backlog-quality-reviewer) (`opus`) |
| Stable epic IDs and the roadmap proposal | [`planning-delivery-roadmaps`](/docs/plugins/tsh-product-management/skills/planning-delivery-roadmaps) | [`roadmap-planner`](/docs/plugins/tsh-product-management/agents/roadmap-planner) (`opus`) — exactly one, never fanned out |
| Jira-ready formatting, verification diffs, baseline content | [`formatting-jira-issues`](/docs/plugins/tsh-product-management/skills/formatting-jira-issues) | [`jira-formatter`](/docs/plugins/tsh-product-management/agents/jira-formatter) (`haiku`) |
| Term candidates and the codebase identifier sweep | [`managing-domain-dictionaries`](/docs/plugins/tsh-product-management/skills/managing-domain-dictionaries) | [`terminology-extractor`](/docs/plugins/tsh-product-management/agents/terminology-extractor) (`sonnet`) |

Workers have only `Read`, `Grep` and `Glob` (the quality reviewer adds `WebSearch` and `WebFetch`). They write no files, ask nobody anything, and reach neither Jira nor a design tool: the orchestrator fetches Jira payloads and Figma extracts itself and passes them into the prompt, along with the Protected Status Policy whenever existing tasks are in play. BA work is never sent to `general-purpose`, `Explore` or any other agent.

**Parallelism is suggested, not automatic.** The orchestrator evaluates the volume — several independent sources, three or more substantial documents, a long transcript, a large backlog for review — proposes how many workers and why, and waits for confirmation. Confirmed parallel calls go out in a single message, at most five workers at once. Extraction fans out one `backlog-extractor` per epic, or two or three small epics per worker; the orchestrator merges the results, renumbers them and writes the file. Roadmap planning never fans out: reconciliation needs the whole epic set in one context.

## Step by step

1. **Create the gate ledger** at `specifications/<workshop-name>/.gates.md`.
2. **Process the transcript** when raw discussion material is supplied: topics, decisions, action items, open questions and exact quotes, saved as `cleaned-transcript.md`. Skipped for structured notes or direct requirements.
3. **Analyse the remaining materials and the baseline** — designs, PDFs (read with `Read`), other documents, and `specifications/projects/<project-name>/task-baseline.md` if it exists. This phase most often justifies parallel workers. A project domain dictionary is consumed as canonical terms when present; otherwise the orchestrator suggests `/tsh-product-management:domain-dictionary`.
4. **Draft the intent brief** — goal, in scope, out of scope, actors, likely epic candidates, baseline overlap, open questions — and run **Gate 0**.
5. **Extract epics and stories** from the approved brief. Each epic is a demonstrable vertical slice with an Epic Delivery Contract; each story has a `Source` field and `GIVEN / WHEN / THEN` acceptance criteria. The draft `extracted-tasks.md` is presented file-first at **Gate 1**.
6. **Run the quality review** automatically after Gate 1, in Lite or Full mode, over a domain model built from the tasks. Every suggestion goes into `quality-review.md` before one disposition question at **Gate 1.5**; accepted suggestions are applied to `extracted-tasks.md`.
7. **Confirm the updated tasks.** The orchestrator summarises what changed and proceeds only on confirmation.
8. **Propose the roadmap.** A single `roadmap-planner` reconciles the confirmed tasks, accepted findings, baseline and any existing roadmap into client-facing outcome waves and an internal coordination view, linked by project-scoped stable epic IDs. The proposal is written to `.roadmap-proposal.md`.
9. **Roadmap Review** — Gate 1.75. Only after the approval is recorded is `specifications/projects/<project-name>/roadmap.md` created or updated. The roadmap is Markdown-only: no Jira releases, custom fields, synchronisation or status changes.
10. **Format for Jira** against the benchmark template, preserving source traceability, and review the formatted `jira-tasks.md` from the file.
11. **Gate 2.** Confirm the target project and the scope of the push, and record the approval — naming the project key — **before** any write call.
12. **Push, verify, archive.** Epics first, then linked stories, each returned key written back into `jira-tasks.md` immediately; existing keys are updated, never recreated. The issues are read back and checked. Then the session artifacts are archived and the project baseline is refreshed.

The workflow ends with exactly one suggested next step — it does not run it. A session that stopped before Gate 2 says which gate it reached, which file holds the state, and how to resume.

### Other entry points

- **Explore Mode** — `/tsh-product-management:explore-materials` reads the materials and writes `specifications/<workshop-name>/workshop-context-summary.md`: context, actors and entities, baseline overlap, likely epic candidates, open questions, and a readiness recommendation. It creates no epics or stories unless the user asks to continue, which hands off to `analyze-materials`.
- **Import** — Jira issue keys, a project key or a JQL query instead of materials skip transcript processing and extraction. [`formatting-jira-issues`](/docs/plugins/tsh-product-management/skills/formatting-jira-issues) imports the issues read-only into `jira-tasks.md`, then the quality review runs over them and the workflow continues from there. Gate 2 applies when local changes are pushed back.

## The gates

| Gate | After | The user decides |
| :-- | :-- | :-- |
| 0 | The intent brief | Is this the right scope, with the right exclusions and candidate epics? |
| 1 | Task extraction | Is this the right epic and story breakdown? |
| 1.5 | Quality review | Which suggestions refine the list, and which are rejected? |
| 1.75 | The roadmap proposal | Are these waves, tracks and stable IDs right? |
| 2 | Jira formatting | Push this, to this project, now? |

Every approval is written to `.gates.md` **before** the action it unlocks; the ledger, not the conversation, is the source of truth, because a long session gets summarised. Gate approvals get one question per call, and large review sets go to a file with one disposition question against it rather than a popup per item. Beyond the gates, the user also confirms parallelisation, answers item-level clarifications, confirms the updated task list after Gate 1.5, approves the sync summary (create / update / skipped) before the push, and decides how to proceed on any failed worker or Jira call.

### The hook behind Gate 2

The plugin ships a `PreToolUse` hook that runs on Atlassian MCP tools. It denies a recognised Jira write while no live ledger has an approved Gate 2 row, or when the write targets a project that row does not name. It also refuses to update an issue marked protected in `jira-tasks.md`. Reads are never gated, Confluence tools are left to the normal permission prompt, and a tool it cannot classify is held with `ask`. Ledgers archived under `sessions/` unlock nothing, so one workshop's approval never carries into the next. The hook is active whichever way the workflow is entered, including a direct `/tsh-product-management:formatting-jira-issues`, and stands down in a repository with no BA artifacts on disk.

That is why the Jira gate stays numbered `2`, and Roadmap Review is `1.75`: the hook matches the row by number.

### Protected statuses

A task whose Jira status is **Done**, **Cancelled** or **PO APPROVE** is immutable everywhere in the workflow: no local edits, no Jira updates, no quality-review suggestions, skipped by formatting and push. Import brings it in read-only, marked `🔒`. A request to change one is refused with a fixed message asking the user to fix the status in Jira and re-import.

## What it leaves behind

| Artifact | Path | Lifetime |
| :-- | :-- | :-- |
| Gate ledger | `specifications/<workshop-name>/.gates.md` | Session |
| Cleaned transcript | `specifications/<workshop-name>/cleaned-transcript.md` | Session |
| Context summary (Explore Mode only) | `specifications/<workshop-name>/workshop-context-summary.md` | Session |
| Intent brief | `specifications/<workshop-name>/intent-brief.md` | Session |
| Epics and stories | `specifications/<workshop-name>/extracted-tasks.md` | Session |
| Quality review and dispositions | `specifications/<workshop-name>/quality-review.md` | Session |
| Roadmap draft | `specifications/<workshop-name>/.roadmap-proposal.md` | Session |
| Jira-ready tasks with keys | `specifications/<workshop-name>/jira-tasks.md` | Session |
| Archived session | `specifications/projects/<project-name>/sessions/<YYYY-MM-DD>-<workshop-name>/` | Project |
| Approved roadmap | `specifications/projects/<project-name>/roadmap.md` | Project |
| Task baseline | `specifications/projects/<project-name>/task-baseline.md` | Project |
| Domain dictionary and its ledger | `specifications/projects/<project-name>/domain-dictionary.md`, `.dictionary-gates.md` | Project |

## The domain dictionary

`/tsh-product-management:domain-dictionary` runs [`managing-domain-dictionaries`](/docs/plugins/tsh-product-management/skills/managing-domain-dictionaries): the canonical business vocabulary of one product, not domain-driven design. Its modes compose as Harvest (term candidates from materials), Reconcile (against a codebase's identifiers, without editing code) and Interview (for what is still missing), with `terminology-extractor` doing the reading. It keeps its own gates — `D1` to `D3` — in `.dictionary-gates.md`, never in `.gates.md`, so a dictionary session never arms the Jira guard. A session's proposal waits in `specifications/<workshop-name>/.dictionary-delta.md` until `D1` approves the merge. The closing handoff points at `/tsh-core:managing-claude-context`, which wires the dictionary into a code repository — see [Project context](./project-context).

## What it needs

- **`tsh-core`**, for the Atlassian MCP server (anything Jira) and the Figma MCP server (design links). Run `/mcp` once to sign in. The workflow checks what the session has up front, and reports design analysis as blocked rather than skipping it. See [Atlassian](/docs/integrations/atlassian) and [Figma](/docs/integrations/figma).
- **Nothing for PDFs** — they are read with the standard `Read` tool. Binary Office files need a PDF, CSV or plain-text export.

Implementation, testing and design work live in other plugins that may not be installed; the workflow names the gap instead of linking into them.
