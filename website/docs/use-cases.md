---
title: Use cases
sidebar_label: Use cases
sidebar_position: 6
description: What Agentic Collections does today, organised by vertical — product management, product engineering, product testing, platform engineering, context management and stacks — with a link to the skill or agent behind each use case.
sources:
  - README.md
  - plugins/tsh-product-management/README.md
  - plugins/tsh-product-management/skills/analyze-materials/SKILL.md
  - plugins/tsh-product-management/skills/explore-materials/SKILL.md
  - plugins/tsh-product-management/skills/orchestrating-business-analysis/SKILL.md
  - plugins/tsh-product-management/skills/extracting-epics-and-stories/SKILL.md
  - plugins/tsh-product-management/skills/reviewing-backlog-quality/SKILL.md
  - plugins/tsh-product-management/skills/formatting-jira-issues/SKILL.md
  - plugins/tsh-product-management/skills/planning-delivery-roadmaps/SKILL.md
  - plugins/tsh-product-management/skills/domain-dictionary/SKILL.md
  - plugins/tsh-product-management/skills/managing-domain-dictionaries/SKILL.md
  - plugins/tsh-product-management/skills/initializing-project-context/SKILL.md
  - plugins/tsh-product-management/skills/navigating-project-context/SKILL.md
  - plugins/tsh-product-management/skills/writing-project-knowledge/SKILL.md
  - plugins/tsh-product-management/agents/discovery-analyst.md
  - plugins/tsh-product-management/agents/roadmap-planner.md
  - plugins/tsh-product-engineering/README.md
  - plugins/tsh-product-engineering/skills/orchestrating-feature-implementation/SKILL.md
  - plugins/tsh-product-engineering/skills/creating-implementation-plans/SKILL.md
  - plugins/tsh-product-engineering/skills/reviewing-ui/SKILL.md
  - plugins/tsh-product-engineering/skills/debugging-code/SKILL.md
  - plugins/tsh-product-engineering/skills/reviewing-code/SKILL.md
  - plugins/tsh-product-engineering/skills/auditing-application-security/SKILL.md
  - plugins/tsh-product-engineering/skills/discovering-technical-context/SKILL.md
  - plugins/tsh-product-engineering/agents/software-engineer.md
  - plugins/tsh-product-engineering/agents/code-reviewer.md
  - plugins/tsh-product-engineering/agents/security-auditor.md
  - plugins/tsh-product-engineering/agents/feature-verifier.md
  - plugins/tsh-product-engineering/agents/ui-capture-worker.md
  - plugins/tsh-product-engineering/agents/ui-reviewer.md
  - plugins/tsh-product-testing/README.md
  - plugins/tsh-product-testing/skills/writing-playwright-e2e-tests/SKILL.md
  - plugins/tsh-product-testing/skills/auditing-accessibility/SKILL.md
  - plugins/tsh-product-testing/agents/e2e-engineer.md
  - plugins/tsh-platform-engineering/README.md
  - plugins/tsh-platform-engineering/skills/implementing-ci-cd-pipelines/SKILL.md
  - plugins/tsh-platform-engineering/skills/implementing-observability/SKILL.md
  - plugins/tsh-platform-engineering/agents/devops-engineer.md
  - plugins/tsh-platform-engineering/agents/infrastructure-auditor.md
  - plugins/tsh-core/README.md
  - plugins/tsh-core/skills/init/SKILL.md
  - plugins/tsh-core/skills/managing-claude-context/SKILL.md
  - plugins/tsh-core/skills/managing-decision-records/SKILL.md
  - plugins/tsh-core/skills/managing-git-worktrees/SKILL.md
  - plugins/tsh-core/skills/writing-technical-documents/SKILL.md
  - plugins/tsh-core/skills/authoring-claude-extensions/SKILL.md
  - plugins/tsh-stack-frontend/skills/implementing-frontend/SKILL.md
  - plugins/tsh-stack-nodejs/skills/implementing-nestjs-api/SKILL.md
  - plugins/tsh-stack-php/agents/php-code-reviewer.md
  - plugins/tsh-stack-serverless/skills/configuring-serverless-service/SKILL.md
  - plugins/tsh-stack-python/skills/writing-data-models/SKILL.md
  - plugins/tsh-stack-aws/skills/auditing-aws-cost/SKILL.md
  - plugins/tsh-stack-gcp/skills/auditing-gcp-cost/SKILL.md
  - plugins/tsh-stack-azure/skills/auditing-azure-cost/SKILL.md
sources_hash: "07260bc33670a682488286e9c549be009ac6923b3c1464246b7200da45966d7b"
---

# Use cases

Each use case below is something a skill or agent in Agentic Collections does today, grouped by vertical. Every one links to the page of the component that does the work.

{/* PHASE2(narrative): page structure (vertical → scenario → problem → what happens) — follows the shape of the Copilot Collections use-cases page; its time-per-task figures were dropped because no source here backs them — decide in Phase 2 whether to keep this shape and whether measured timings for Agentic Collections exist */}

## Product Management

### Workshop material → Jira-ready backlog

A discovery workshop leaves transcripts, Figma files and PDFs behind, and turning them into a backlog means many decisions that each need a human. In a long session those decisions are at risk: the conversation gets summarized, and a remembered approval does not survive that.

[`/tsh-product-management:analyze-materials`](/docs/plugins/tsh-product-management/skills/analyze-materials) takes a transcript path, a Figma or FigJam link, a PDF or a folder of documents and runs the workflow in [`orchestrating-business-analysis`](/docs/plugins/tsh-product-management/skills/orchestrating-business-analysis). The heavy reading goes to read-only worker subagents. The result is an intent brief, epics as independently demonstrable vertical slices, and user stories with source traceability and GIVEN/WHEN/THEN acceptance criteria. Five human review gates stand between the material and Jira:

| Gate | After | You decide |
| :-- | :-- | :-- |
| 0 | The intent brief | Is this the right scope? |
| 1 | Extraction | Is this the right breakdown? |
| 1.5 | Quality review | Which suggestions land? |
| 1.75 | The roadmap proposal | Are these the right waves? |
| 2 | Jira formatting | Push, to this project, now? |

Every approval is written to `specifications/<workshop-name>/.gates.md` before the action it unlocks. Gate 2 is enforced by a hook: it denies Atlassian write calls while the Gate 2 row is unapproved, and refuses to update an issue whose status is Done, Cancelled or PO APPROVE.

**Start:** `/tsh-product-management:analyze-materials <path or link>` · Walkthrough: [Business analysis](/docs/workflows/business-analysis)

### Explore the material before committing to scope

Sometimes the right first step is to understand the material, not to cut tickets from it. [`/tsh-product-management:explore-materials`](/docs/plugins/tsh-product-management/skills/explore-materials) reads the workshop material and produces a business-context summary with likely epic candidates and open questions, without creating any backlog items. The synthesis can be delegated to the [`discovery-analyst`](/docs/plugins/tsh-product-management/agents/discovery-analyst) agent, which also reports baseline overlap and contradictions between sources; its results always come back through your conversation before anything moves toward extraction.

**Start:** `/tsh-product-management:explore-materials <path or link>`

### Review an existing Jira backlog for gaps

`analyze-materials` also accepts Jira issue keys or a project key. It imports the existing backlog into the same local format for iteration. [`reviewing-backlog-quality`](/docs/plugins/tsh-product-management/skills/reviewing-backlog-quality) then builds a domain model of actors, entities and their relationships from the tasks and runs Lite or Full analysis passes over it, looking for gaps, missing edge cases and delivery-readiness problems.

Every finding becomes a suggestion you accept or reject individually. All suggestions are written to `quality-review.md` before you are asked anything, and every disposition is recorded, rejected ones included. Tasks with a protected status (Done, Cancelled, PO APPROVE) are filtered out before the passes run.

**Start:** `/tsh-product-management:analyze-materials <issue keys or project key>`

### An outcome-based delivery roadmap

[`planning-delivery-roadmaps`](/docs/plugins/tsh-product-management/skills/planning-delivery-roadmaps) reconciles the approved epics, the accepted quality findings, the project baseline and any existing roadmap into one Markdown roadmap per project. It has client-facing outcome waves and an internal coordination view, linked by project-scoped stable epic IDs. It creates no Jira data and changes no statuses. The [`roadmap-planner`](/docs/plugins/tsh-product-management/agents/roadmap-planner) agent proposes the waves, and you approve them at Gate 1.75.

**Start:** runs inside the `analyze-materials` workflow, after the task list is confirmed and before Jira formatting.

### One vocabulary for the product

[`/tsh-product-management:domain-dictionary`](/docs/plugins/tsh-product-management/skills/domain-dictionary) produces and maintains a per-product domain dictionary: the canonical business-term glossary, not domain-driven design. [`managing-domain-dictionaries`](/docs/plugins/tsh-product-management/skills/managing-domain-dictionaries) runs it in Harvest, Reconcile and Interview modes, checks it with eleven review passes, and reconciles it against a live codebase without ever editing that codebase.

**Start:** `/tsh-product-management:domain-dictionary` with a project name, a workshop directory, a repository path to reconcile against, or nothing.

## Product Engineering

### Implement a ticket from a committed plan

Subagents never see your conversation, so a plan that lives only in chat cannot be reviewed in a pull request or executed by an implementer. [`creating-implementation-plans`](/docs/plugins/tsh-product-engineering/skills/creating-implementation-plans) writes the plan as a file at `specifications/<task-id>/<task-name>.plan.md`: phased tasks that each name their files and a verifiable Definition of Done, technical context persisted for the implementers, and explicit parallel groups.

[`orchestrating-feature-implementation`](/docs/plugins/tsh-product-engineering/skills/orchestrating-feature-implementation) executes it from the main conversation. Non-trivial work starts only after you have read the plan. Each task goes to the [`software-engineer`](/docs/plugins/tsh-product-engineering/agents/software-engineer) or [`ui-engineer`](/docs/plugins/tsh-product-engineering/agents/ui-engineer) subagent, in parallel only when the plan marks the tasks as one group and their files are disjoint. Every task report is gated, and the flow stops on any material deviation from the plan. The work closes with [`code-reviewer`](/docs/plugins/tsh-product-engineering/agents/code-reviewer) and [`feature-verifier`](/docs/plugins/tsh-product-engineering/agents/feature-verifier) running in parallel: one reviews the code, the other executes the plan's verification document against the running app, with per-scenario evidence.

**Start:** ask Claude to "implement this ticket", or run `/tsh-product-engineering:orchestrating-feature-implementation` · Walkthrough: [Feature implementation](/docs/workflows/feature-implementation)

### UI that matches the Figma design

A clean build does not prove that a screen matches its design. [`reviewing-ui`](/docs/plugins/tsh-product-engineering/skills/reviewing-ui) runs one verification pass: [`ui-capture-worker`](/docs/plugins/tsh-product-engineering/agents/ui-capture-worker) collects `actual.png`, `computed-styles.json` and `a11y-snapshot.yml` from the running app with the Playwright CLI, and [`ui-reviewer`](/docs/plugins/tsh-product-engineering/agents/ui-reviewer) judges them against the Figma design. The verdict is PASS, FAIL or VERIFICATION NOT RUN, with a complete difference table. The pass is read-only and never fixes code.

During feature implementation, every Figma-backed UI task goes through this gate, iterated up to five times per item, before final verification starts. Design fetching needs the Figma MCP server that `tsh-core` bundles; until you sign in, the reviewer reports VERIFICATION NOT RUN instead of guessing at a design.

**Start:** ask "does this page match the design?", or run `/tsh-product-engineering:reviewing-ui` · Walkthrough: [UI verification](/docs/workflows/ui-verification)

### Fix a bug at its root cause

[`debugging-code`](/docs/plugins/tsh-product-engineering/skills/debugging-code) treats a bug as fixed only when its cause is named, removed and guarded by a test that failed before the fix and passes after it. It pins the symptom, reproduces it, secures a failing test (existing, corrected or new), states the root cause as a causal chain with evidence, and measures how far the fix reaches before applying it minimally. It then reports sibling occurrences of the same faulty pattern.

**Start:** describe the wrong behaviour, or run `/tsh-product-engineering:debugging-code` · Walkthrough: [Debugging](/docs/workflows/debugging)

### Code review before merge

[`reviewing-code`](/docs/plugins/tsh-product-engineering/skills/reviewing-code) reads the plan and requirements before the diff. It executes the project's tests, linters and build itself, and never accepts "tests pass" from an implementation report. Every review runs a universal security baseline of framework-agnostic OWASP classes on top of the project's own rules, and checks for high-risk anti-patterns such as N+1 access and in-memory pagination. When a stack skill for the change's framework is installed, the review loads it and applies its checklist too. Every finding carries a severity, the file and line, the consequence and the minimum correction. The [`code-reviewer`](/docs/plugins/tsh-product-engineering/agents/code-reviewer) agent runs the same review read-only.

**Start:** ask "is this ready to merge?", or run `/tsh-product-engineering:reviewing-code`

### A security audit of a whole service

A review reads one change; [`auditing-application-security`](/docs/plugins/tsh-product-engineering/skills/auditing-application-security) reads a whole service or a named surface. It maps the attack surface entry point by entry point, runs only the security scanners the project already has and never installs one, and applies the same baseline classes as the code review, with OWASP Top 10, ASVS or pen-test preparation on top when you name one. Dependency advisories are triaged by reachability and exploitability before they get a severity, so an advisory in code the service never reaches does not crowd out a real finding. The report ends with what was not checked. The [`security-auditor`](/docs/plugins/tsh-product-engineering/agents/security-auditor) agent runs the same audit read-only.

**Start:** ask for a security audit or "which of these advisories actually affect us?", or run `/tsh-product-engineering:auditing-application-security`

### Follow the project's conventions, not generic ones

[`discovering-technical-context`](/docs/plugins/tsh-product-engineering/skills/discovering-technical-context) establishes which conventions a change must follow before it is written, in priority order: the plan's persisted technical context, then project instructions (`CLAUDE.md`, `.claude/rules`, decision records), then existing codebase patterns, then external documentation.

**Start:** ask "how does this project do X?", or run `/tsh-product-engineering:discovering-technical-context`

## Product Testing

### End-to-end tests from acceptance criteria

[`@tsh-product-testing:e2e-engineer`](/docs/plugins/tsh-product-testing/agents/e2e-engineer) writes Playwright tests from acceptance criteria or a plan task. Given only a Jira issue key, it reads the criteria through the Atlassian MCP tools that `tsh-core` bundles. It confirms locators against the running app with the Playwright CLI before the first test run, and says so in the report when it could not because the dev server was unreachable. It reports a test done only after three or more consecutive headless passes. When the application itself is broken, the test is marked `test.fixme('BUG: …')` and the bug is reported; the agent never modifies application code and never weakens an assertion to go green.

**Start:** `@tsh-product-testing:e2e-engineer` with a Jira issue key, a plan task or the acceptance criteria

### A suite that stops flaking

[`writing-playwright-e2e-tests`](/docs/plugins/tsh-product-testing/skills/writing-playwright-e2e-tests) holds the rules that keep a test reliable: user-visible locators (`getByRole`, `getByLabel`, `getByText`), auto-waiting assertions instead of `waitForTimeout()` or `networkidle`, unique test data per run so tests are parallel-safe, and mocks only at genuinely external boundaries. A bounded debug loop with explicit iteration limits and flake detection handles a test that fails sometimes. The same `e2e-engineer` agent diagnoses a flaky suite.

**Start:** describe the flaky test, or run `/tsh-product-testing:writing-playwright-e2e-tests`

### An accessibility audit a developer can act on

[`auditing-accessibility`](/docs/plugins/tsh-product-testing/skills/auditing-accessibility) audits a page, component or flow against WCAG 2.1 AA. Every finding names its success criterion and is located in the source or reproduced in a browser. A keyboard-inoperable interactive element is a blocker, not a nit. The audit checks light and dark themes, and LTR and RTL where the app is localized, and triages axe-core output. Building accessible components is a separate job, owned by `ensuring-accessibility` in `tsh-stack-frontend`.

**Start:** ask for an accessibility audit, or run `/tsh-product-testing:auditing-accessibility`

## Platform Engineering

### Infrastructure changes built and validated, not applied

[`@tsh-platform-engineering:devops-engineer`](/docs/plugins/tsh-platform-engineering/agents/devops-engineer) implements Terraform modules, pipelines, Kubernetes workloads, observability and secrets. It carries a mutation lock: no `terraform apply`, no `kubectl apply` against a real cluster, no `helm install`. Every change is validated with `terraform plan`, `validate`, `kubectl apply --dry-run=server` or `helm template`, and the apply instructions go to a human in the report. The single exception is an explicit, specific instruction to run one named mutating command; blanket permission earlier in a conversation does not count. Every proposal carries a cost estimate and flags a projected increase above 10%.

**Start:** `@tsh-platform-engineering:devops-engineer` with a plan task, a ticket or a description of the change

### Pipelines without stored cloud keys

[`implementing-ci-cd-pipelines`](/docs/plugins/tsh-platform-engineering/skills/implementing-ci-cd-pipelines) designs pipelines on GitHub Actions, GitLab CI, Bitbucket Pipelines, Azure Pipelines or Jenkins: stage structure and caching, rolling, blue-green or canary deployment, OIDC federation for cloud credentials instead of stored keys, monorepo affected-only builds, and the plan-artifact and approval gates an infrastructure-as-code pipeline requires.

**Start:** ask for the pipeline change, or run `/tsh-platform-engineering:implementing-ci-cd-pipelines`

### Monitoring an on-call rotation can rely on

[`implementing-observability`](/docs/plugins/tsh-platform-engineering/skills/implementing-observability) sets up metrics, logs, traces and alerting: RED and USE metrics, SLOs with error budgets, alerts that fire on user-visible symptoms and link to runbooks, and structured logging with trace correlation.

**Start:** ask to add monitoring or define SLOs, or run `/tsh-platform-engineering:implementing-observability`

### An infrastructure audit with ranked findings

[`@tsh-platform-engineering:infrastructure-auditor`](/docs/plugins/tsh-platform-engineering/agents/infrastructure-auditor) audits security exposure, cost waste and operational-practice gaps. It reads the IaC and CI configuration, validates against live cloud state where credentials allow, detects drift and shadow resources, and returns a severity-ranked findings report. It never changes a file or cloud state. When it cannot authenticate to a named account, it says so and marks the report as code-only. The cloud-specific cost and tagging audits live in the [stack plugins](#stacks).

**Start:** `@tsh-platform-engineering:infrastructure-auditor` with the repository, account or project and the focus

## Context management

### Set up Claude Code's context in a repository

[`/tsh-core:init`](/docs/plugins/tsh-core/skills/init) takes a repository from any starting state to a complete set of context files: a root `CLAUDE.md` (nested ones where ownership demands), path-scoped rules in `.claude/rules/`, a decision-record archive with its index, and a maintenance section in `CLAUDE.md` naming the skill that keeps each artifact current. It is safe to re-run: the second pass is a repair. It works by running [`managing-claude-context`](/docs/plugins/tsh-core/skills/managing-claude-context) and its neighbours in order. `managing-claude-context` records conventions the team already holds and asks rather than inventing one when the codebase is ambiguous.

**Start:** `/tsh-core:init` inside the repository · Afterwards, ask when Claude keeps ignoring a convention, or the memory files have drifted from the code

### Decision records that say which decisions bind

[`managing-decision-records`](/docs/plugins/tsh-core/skills/managing-decision-records) owns the shape and lifecycle of an ADR: the four-section format, the status vocabulary, numbering, superseding, and keeping the index in step. Only `Accepted` records bind; every other status is history you read but never obey. No skill sets a record's status: marking a decision `Accepted` stays a human call, and the skill proposes one and names who decides.

**Start:** ask to record or supersede a decision, or run `/tsh-core:managing-decision-records`

### A shared knowledge base for the whole project

A project's scope, decisions, vocabulary and owners can live in one `<project>-context` repository. [`/tsh-product-management:initializing-project-context`](/docs/plugins/tsh-product-management/skills/initializing-project-context) scaffolds it as a local git repository, publishes it to Bitbucket, GitHub or any git host after asking, and connects code repositories to it: committed for the team's own repositories, local-only for a client's. Connecting a repository enables the plugin there, so an engineer or tester gets the knowledge-base skills without installing anything.

From then on, [`navigating-project-context`](/docs/plugins/tsh-product-management/skills/navigating-project-context) reads the knowledge base before work that depends on it and cites the file, its last change and its owner behind every project fact. [`writing-project-knowledge`](/docs/plugins/tsh-product-management/skills/writing-project-knowledge) adds or updates a document in the owning workspace, on its own branch, creating, committing and pushing only after asking, and names the owner who reviews it.

**Start:** `/tsh-product-management:initializing-project-context` in the folder where the project should live · Walkthrough: [Project context](/docs/workflows/project-context)

## Stacks

Stack plugins add what changes with the language, framework or cloud, and install at project scope. They plug into the work above: for example, `reviewing-code` loads whichever stack skill matches the change's framework and applies its checklist.

- **Frontend:** [`implementing-frontend`](/docs/plugins/tsh-stack-frontend/skills/implementing-frontend) covers any change to frontend application code, React today, with or without a design, and requires a Figma read before markup when a design exists.
- **Node.js:** [`implementing-nestjs-api`](/docs/plugins/tsh-stack-nodejs/skills/implementing-nestjs-api) guides implementation and review of NestJS 11 REST APIs with `@nestjs/cqrs` and TypeORM 0.3.
- **PHP:** [`@tsh-stack-php:php-code-reviewer`](/docs/plugins/tsh-stack-php/agents/php-code-reviewer) reviews PHP and Symfony changes against the project's own PHP and Symfony versions, runs the project's linters and static analysis, and returns a structured findings report.
- **Serverless:** [`configuring-serverless-service`](/docs/plugins/tsh-stack-serverless/skills/configuring-serverless-service) defines an AWS Lambda service on OSLS with least-privilege IAM without wildcard resources, per-function reserved concurrency, secrets resolved at runtime, and assertions over the packaged CloudFormation template.
- **Python:** [`writing-data-models`](/docs/plugins/tsh-stack-python/skills/writing-data-models) governs data modelling with Pydantic v2, dataclasses, SQLModel and SQLAlchemy 2.0.
- **Cloud cost audits:** [`auditing-aws-cost`](/docs/plugins/tsh-stack-aws/skills/auditing-aws-cost), [`auditing-gcp-cost`](/docs/plugins/tsh-stack-gcp/skills/auditing-gcp-cost) and [`auditing-azure-cost`](/docs/plugins/tsh-stack-azure/skills/auditing-azure-cost) read the infrastructure code first, validate it against the live account, project or subscription with read-only calls, find drift and shadow resources, check tag or label compliance, attribute measured spend, and produce a saved report.

## Foundation: `tsh-core`

Some work is the same whatever your role and stack, and lives in [`tsh-core`](/docs/plugins/tsh-core/):

- **Parallel checkouts:** [`managing-git-worktrees`](/docs/plugins/tsh-core/skills/managing-git-worktrees) creates a worktree from a freshly fetched base branch on `origin`, lists worktrees, and removes one precisely identified worktree, each with explicit confirmation and verification after the change.
- **Documents people read:** [`writing-technical-documents`](/docs/plugins/tsh-core/skills/writing-technical-documents) applies TSH's writing standard to a README, CHANGELOG, ADR, PR description, runbook, ticket, bug report or test plan: lead with the conclusion, verify every claim against the source, and cut what does not change the reader's decision.
- **Your own extensions:** [`authoring-claude-extensions`](/docs/plugins/tsh-core/skills/authoring-claude-extensions) decides whether a need calls for a skill, a subagent, a hook or a plugin, and then writes it.
