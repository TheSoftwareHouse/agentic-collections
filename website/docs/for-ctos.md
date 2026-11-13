---
title: For CTOs
sidebar_label: For CTOs
sidebar_position: 7
description: What Agentic Collections changes in a team's delivery, where people stay in charge, and what adopting it involves.
sources:
  - README.md
  - CLAUDE.md
  - LICENSE
  - .claude-plugin/marketplace.json
  - plugins/tsh-product-management/README.md
  - plugins/tsh-product-engineering/README.md
  - plugins/tsh-product-testing/README.md
  - plugins/tsh-platform-engineering/README.md
  - plugins/tsh-core/README.md
  - plugins/tsh-product-engineering/skills/orchestrating-feature-implementation/SKILL.md
  - plugins/tsh-product-engineering/skills/creating-implementation-plans/SKILL.md
  - plugins/tsh-product-engineering/skills/reviewing-code/SKILL.md
  - plugins/tsh-product-engineering/skills/auditing-application-security/SKILL.md
  - plugins/tsh-product-engineering/skills/reviewing-ui/SKILL.md
  - plugins/tsh-product-engineering/skills/discovering-technical-context/SKILL.md
  - plugins/tsh-product-testing/skills/auditing-accessibility/SKILL.md
  - plugins/tsh-platform-engineering/agents/devops-engineer.md
  - plugins/tsh-product-engineering/skills/debugging-code/SKILL.md
  - plugins/tsh-core/skills/init/SKILL.md
  - plugins/tsh-core/skills/managing-decision-records/SKILL.md
  - plugins/tsh-product-management/skills/navigating-project-context/SKILL.md
sources_hash: "9c06f70eec3549b5860489475d1c8b59ad2048bc579c0c7767542e667f8472d3"
---

# For CTOs

{/* PHASE2(narrative): whole page — rewritten from the Copilot Collections "For CTOs" page; its section order, headings and claims are inherited, while every product statement was rewritten from this repository's sources — Phase 2 writes the narrative for Agentic Collections and replaces the inherited figures with ones measured on it */}

Agentic Collections is a Claude Code plugin marketplace used daily by **300+ engineers** at The Software House across **50+ commercial projects** — delivering a **30% average lead time reduction**. {/* TODO(marketing): confirm before publishing */}

:::brand TL;DR:

- Only 10% of teams see real gains from AI coding tools - the gap is structural, not technological {/* TODO(marketing): confirm before publishing */}
- Agentic Collections gives Claude Code TSH's way of working as installable skills and agents: committed plans, human review gates, and evidence before anything is called done
- 300+ engineers at TSH use it daily across 50+ commercial projects with great result: average lead time down 30% {/* TODO(marketing): confirm before publishing */}
- Covers the full lifecycle: discovery workshop → Jira-ready backlog → implementation → code review and functional verification, plus end-to-end tests and infrastructure
- Open source, MIT licence

:::

## The AI productivity gap is real and structural

Gartner found that only **10% of software engineers** see meaningful productivity gains from AI coding assistants. The other 90% are using the same tools and getting inconsistent results. {/* TODO(marketing): confirm before publishing */}

When engineers use AI ad-hoc the results vary by individual. You get pockets of acceleration alongside unchanged delivery speed, inconsistent code quality, and a team that's learned to trust AI selectively and unpredictably. {/* TODO(marketing): confirm before publishing */} {/* PHASE2(narrative): ad-hoc AI paragraph — kept from the Copilot Collections page, an industry observation no source here backs — replace with TSH's own framing or cite a source */}

**Agentic Collections** is a structured response to this problem. It does not replace your process: local repository rules outrank its skills, and where a project defines its own delivery workflow, Agentic Collections runs inside it, not instead of it. Plans, gate approvals and review reports are files in the repository, and the steps that cannot be undone wait for a person: the Jira push waits for an approved gate, implementation waits until you have read the plan, and infrastructure changes are handed to a human to apply, unless a person explicitly names the one mutating command to run.

---

## What it actually changes

Agentic Collections is not an application. It is plugins — skills, agents, hooks and MCP servers — that Claude Code loads, and they change how work moves through a team, from workshop material to reviewed, verified code.

**Product Management**: discovery workshop material — transcripts, Figma, PDFs, codebase context — becomes Jira-ready epics and user stories with GIVEN/WHEN/THEN acceptance criteria, a systematic quality review and an outcome-based delivery roadmap, behind five human review gates. While a business-analysis session is open in the repository, a hook refuses Jira writes to a project until its push gate (Gate 2) is approved for that project, and never updates an issue that is Done, Cancelled or PO APPROVE. Context gathering that used to take 30–60 minutes takes 3 minutes. {/* TODO(marketing): confirm before publishing */}

**Product Engineering**: implementation runs from a committed plan file. Implementer subagents execute its tasks, in parallel where the plan allows, and the work closes with code review and functional verification running in parallel. Before a change is written, its conventions are established in a fixed order: the plan's technical context, the project's own instructions and decision records, existing codebase patterns, and only then external documentation. Every Figma-backed UI task passes a design verification gate, and a bug is fixed at its root cause with a regression test that failed before the fix.

**Product Testing**: Playwright end-to-end tests written from acceptance criteria and proven with three or more consecutive headless passes, and WCAG 2.1 AA audits that name the success criterion behind every finding. The same accessibility criteria apply while a component is being built, because an audit that comes late turns every finding into rework.

**Platform Engineering**: Terraform modules, pipelines with OIDC and plan gates, Kubernetes workloads, observability with SLOs, and secrets management. Infrastructure changes are validated, not applied: every change is checked with `plan`, `validate`, `--dry-run=server` or `template`, the `devops-engineer` agent runs a mutating command only on an explicit instruction naming that command, and every proposal carries a cost estimate.

**Context management**: `/tsh-core:init` sets up the `CLAUDE.md` files, path-scoped rules and decision-record index Claude Code loads in a repository, and a project's shared knowledge base gives every connected repository the same decisions, vocabulary and owners, cited by file, last change and owner.

Security is part of every code review: the review runs a universal security baseline of framework-agnostic OWASP classes on top of the project's own rules and the installed stack skill's checks. A whole service gets a separate, read-only security audit that runs only the scanners the project already has, applies OWASP Top 10, ASVS or pen-test preparation when asked, and triages dependency advisories by reachability before severity.

---

## The numbers, from production use

{/* TODO(marketing): confirm before publishing */}

These aren't benchmark numbers. They come from 300+ engineers using the framework daily across 50+ commercial projects at The Software House. {/* TODO(marketing): confirm before publishing */}

| What changes | Measured impact |
| --- | --- |
| Average lead time | **30% reduction** {/* TODO(marketing): confirm before publishing */} |
| Context gathering time | 60–80% faster {/* TODO(marketing): confirm before publishing */} |
| Planning time | 50–70% faster {/* TODO(marketing): confirm before publishing */} |
| UI defects reaching QA | 70–90% reduction {/* TODO(marketing): confirm before publishing */} |
| Design-to-code accuracy | 95–99% {/* TODO(marketing): confirm before publishing */} |
| E2E test flakiness | 50–80% reduction {/* TODO(marketing): confirm before publishing */} |
| Onboarding time for new engineers | 40–60% reduction {/* TODO(marketing): confirm before publishing */} |

The lead time figure is the headline, but the onboarding number often surprises CTOs most. A structured framework means new engineers aren't learning your way of working from scratch the framework is the way of working. {/* TODO(marketing): confirm before publishing */}

---

## Who uses it and how

{/* PHASE2(narrative): audience split (junior/mid vs senior/leads) — taken from the Copilot Collections page, with each benefit rewritten from this repository's sources — Phase 2 decides whether to address each discipline instead */}

Each discipline installs its own plugin, so a product manager, an engineer, a tester and a platform engineer each get the workflow for their own job.

**Junior and mid-level engineers** get guardrails. Every plan task names its files and a verifiable Definition of Done, conventions come from the project's own instructions and codebase before any external documentation, and a bug fix needs a named root cause and a failing test before the code changes.

**Senior engineers and tech leads** get leverage and keep judgment. They read the plan before implementation starts. Code review is evidence-based: the reviewer runs the tests, linters and build itself and reports every finding with a severity, file and line, consequence and minimum correction. Decisions stay a human call: no skill marks a decision record `Accepted`, and no backlog reaches Jira without an approved gate.

---

## What adoption looks like

Agentic Collections installs into Claude Code v2.1 or newer from its marketplace. There is nothing to build or host: the plugins are mostly Markdown and JSON that Claude Code loads, plus the few hook and helper scripts some skills run, and installing never copies plugin files into your project.

Core and discipline plugins install at user scope and travel with each person. Stack plugins install at project scope and are committed to the repository's `.claude/settings.json`, so everyone who works on the repository gets the same set. Teammates receive an update when a plugin's version is bumped and they run `/plugin update`.

A typical rollout at TSH runs in three phases: {/* TODO(marketing): confirm before publishing */}

- **Install and orient** (day 1) — engineers install the plugins, read the workflow overview, run their first agent interaction on a real ticket.
- **First sprint** (week 1–2) — one team runs the full Product Management → Product Engineering → Product Testing loop on a real project. Friction points surface and get resolved.
- **Team-wide adoption** (week 3–4) — the plugins become the default way of working. Leads review output quality, calibrate to project standards.

{/* PHASE2(narrative): the original closed this section with "self-explanatory for engineers who already use GitHub Copilot" — dropped because it describes the Copilot setup and no source here backs an equivalent claim — Phase 2 decides whether a sentence about Claude Code users belongs here */}

---

## Why TSH built this in the open

The Software House is a 300-person product engineering firm. {/* TODO(marketing): confirm before publishing */}

We built Agentic Collections to solve our own problem - how to get consistent, high-quality AI-assisted delivery across a large, distributed team working on complex commercial projects. {/* TODO(marketing): confirm before publishing */} {/* PHASE2(narrative): motivation paragraph — kept from the Copilot Collections page with the product name swapped; no source here states the motive — Phase 2 confirms or rewrites it */}

We open-sourced it because the problem is structural and universal. Every engineering team using AI tools is navigating the same gap between individual capability and team-level consistency. We've done the work to close that gap. Sharing the framework costs us nothing and helps the industry get there faster. {/* TODO(marketing): confirm before publishing */} {/* PHASE2(narrative): open-source rationale — kept from the Copilot Collections page; no source here states it — Phase 2 confirms or rewrites it */}

The 30% lead time figure comes from our own delivery data. We have skin in the game. {/* TODO(marketing): confirm before publishing */}

---

## Evaluate it for your team

The repository is public and the plugins are MIT-licensed. You need Claude Code v2.1 or newer to run them.

- [Read the documentation](/docs/) — understand how the plugins fit together before committing to anything.
- [See the use cases](/docs/use-cases) — what each vertical does today, with the skill or agent behind it.
- [Get the repo](https://github.com/TheSoftwareHouse/agentic-collections) — install it in an afternoon, run it against a real ticket, see what changes. {/* TODO(marketing): confirm before publishing */}

:::brand

If you want to talk through fit for your team's specific context, reach out to us at [hello@tsh.io](mailto:hello@tsh.io). We'd love to hear from you.

:::
