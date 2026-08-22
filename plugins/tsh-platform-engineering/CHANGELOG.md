# Changelog

All notable changes to `tsh-platform-engineering` are documented here, following
[Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/) and
[Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-08-22

First content release. Ports the DevOps collection from `copilot-collections`,
restructured for Claude Code.

### Added

- **Seven skills**: `implementing-terraform-modules`, `implementing-ci-cd-pipelines`,
  `deploying-to-kubernetes`, `implementing-observability`, `managing-secrets`,
  `optimizing-cloud-cost`, `designing-multi-cloud-architecture`.
- **Two agents**: `devops-engineer`, which builds and validates infrastructure changes
  under an explicit mutation lock, and `infrastructure-auditor`, a read-only
  security, cost and practice audit.
- **`shared/discovering-infrastructure-context.md`** — one copy of the platform, IaC
  dialect, cloud, version-pin, policy and GitOps detection logic, loaded by every
  skill through `${CLAUDE_PLUGIN_ROOT}`.
- **`.mcp.json`** with `context7` and the AWS Labs `aws-documentation` server, both
  read-only.

### Split along the cloud boundary

Cloud-specific content moved out to `tsh-stack-aws`, `tsh-stack-gcp` and
`tsh-stack-azure`, leaving this plugin cloud-agnostic. The reasoning: a repository has one cloud, and the install model
already separates the two — a discipline plugin travels with the engineer at user scope,
a stack plugin with the repository at project scope. An AWS project now installs AWS
content and nothing else.

- **Moved out**: `aws-modules.md` and `gcp-modules.md` became
  `implementing-aws-terraform` and `implementing-gcp-terraform`; `aws-cost-audit.md`,
  `gcp-cost-audit.md` and `audit-report-format.md` became `auditing-aws-cost` and
  `auditing-gcp-cost`, each carrying its own procedure and report format so it stands
  alone.
- **Kept here**: the audit-independent cost framework, module structure, state and
  Terragrunt, pipelines, Kubernetes, observability, secrets, and all cross-cloud
  comparison — `designing-multi-cloud-architecture` needs every provider's tables in
  one place, so it cannot be split by cloud.
- **Azure moved too**, into `tsh-stack-azure`. Its 87-line modules reference became
  `implementing-azure-terraform`, and `auditing-azure-cost` was written from scratch —
  `copilot-collections` had cost prompts for AWS and GCP only, so there was no Azure
  counterpart to port.
- **No delegation instructions.** Nothing here tells the model to invoke a cloud
  plugin's skill: descriptions carry the routing, as `implementing-nestjs-api` and
  `reviewing-code` already do. A pointer into a project-scope plugin from a user-scope
  one dangles on every repository that has no cloud plugin installed.

### Changed from the copilot-collections originals

- **The four internal implementation prompts** — Terraform, pipeline, Kubernetes,
  observability — are folded into the procedure sections of their matching skills
  rather than shipping as four near-duplicate routing entries.
- **The AWS and GCP cost-analysis prompts** became `auditing-aws-cost` and
  `auditing-gcp-cost` in the new `tsh-stack-aws` and `tsh-stack-gcp` plugins. This
  plugin keeps the cloud-agnostic framework in `optimizing-cloud-cost` — pricing
  models, storage tiering, tagging governance, right-sizing method, and the
  cost-impact estimate every proposal carries — and no longer performs account
  audits.
- **The infrastructure-audit prompt** became the `infrastructure-auditor` agent, with
  the procedure in the agent body rather than a companion skill.
- **The mandatory `tsh-architect` sub-agent delegation was dropped.** No architect
  agent exists in this marketplace, and cross-plugin agent references cannot be
  relied on. The three-option output contract it fed — Golden Path, Cost-Optimized,
  Velocity — is kept in `devops-engineer`.
- **The human-approval-record precondition was dropped.** It validated a field set
  that TSH's plan format here does not carry, so the check could only ever fail
  closed. The narrower mutation lock replaces it: no `apply`, `destroy`, `install` or
  `delete` without explicit per-command authorization.
- **Cloud MCP servers moved to the cloud plugins.** This plugin bundles `context7`
  only. `aws-documentation` ships in `tsh-stack-aws`; `gcp-gcloud`,
  `gcp-observability` and `gcp-storage` ship in `tsh-stack-gcp`. A consequence worth
  having: a GCP repository never starts an AWS server, and the one server that can
  mutate infrastructure is scoped to the repository whose cloud it belongs to.
- **Cross-plugin file dependencies were severed.** `tsh-technical-context-discovering`
  and `tsh-codebase-analysing` references are replaced by this plugin's own shared
  context file and by IaC-analysis steps inside the audit agent and cost skill.
  Name-based references to `tsh-core` are used where a core skill already owns the
  outcome: `/tsh-core:managing-decision-records` when a provider or topology choice is
  made, and `/tsh-core:writing-technical-documents` for audit and cost reports that
  leave the team. `tsh-core` is assumed installed — it depends on nothing and everyone
  has it.
- **The mandatory-tag set was reconciled.** The original skill and its reference
  disagreed; the reference's "Core 5" — `CostCenter`, `Environment`, `Service`,
  `Owner`, `DataClass` — is canonical, matching what both cost prompts already used.
- **Every source file over ~150 lines was split** into a `SKILL.md` plus `references/`
  with a Load-when column, per this marketplace's progressive-disclosure rule.
- **VS Code-specific frontmatter was translated**: `vscode/askQuestions` becomes
  `AskUserQuestion`, the model list becomes a single `model`, and the
  `sequential-thinking` MCP mandate is dropped in favour of extended thinking.
