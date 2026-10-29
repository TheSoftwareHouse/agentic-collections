---
name: auditing-application-security
description: "Audits an application's code and dependencies for security across a whole service or a named surface — not a single change — and triages scanner and advisory output into a severity-ranked report. Runs only the security scanners the project already has, never installs them, and applies an optional standard (OWASP Top 10, ASVS, pen-test prep) on top of the universal baseline. Use for a security audit, posture review, OWASP or ASVS assessment, pen-test preparation, or triaging Dependabot, CVE or SAST findings. Reviewing a single change set before merge is reviewing-code; infrastructure and cloud posture is tsh-platform-engineering's infrastructure-auditor."
when_to_use: "Trigger on: a security or application-security audit of a service or codebase, a security posture review, an OWASP Top 10 or ASVS assessment, pen-test preparation, 'how exposed are we', or triaging the output of a SAST scanner, npm/pnpm/pip/composer audit, Dependabot, or a CVE advisory. Reports findings and never fixes code, and runs only the scanners already installed. Reviewing one pasted diff or PR against its plan before merge is reviewing-code; auditing IaC, IAM or cloud configuration is tsh-platform-engineering's infrastructure-auditor."
user-invocable: true
---

# Auditing Application Security

A review reads a change; an audit reads a **surface**. The job is an accurate,
prioritized picture of where a service is exposed, that someone can act on — the whole
codebase or a named part of it, not one diff. Report findings; never fix code.

## Applicability and Precedence

- **The universal baseline is the floor.** The class catalog lives in
  [`reviewing-code`'s security-review-checklist](${CLAUDE_PLUGIN_ROOT}/skills/reviewing-code/references/security-review-checklist.md)
  — broken access control, injection, sensitive-data exposure and the rest. This skill
  applies those classes across a whole surface instead of a single change.
- **The project's own security rules outrank this skill.** A client ruleset, a
  `SECURITY.md`, a `.claude/` security skill, or a stated conformance target is applied
  first; this audit fills what it leaves unstated.
- **A named standard extends the baseline on request.** When the ask names a bar —
  OWASP Top 10 in full, ASVS L1/L2, pen-test preparation — apply it and say which. With
  nothing named, the baseline is the bar.
- **Stack depth on top.** Where a stack skill is available this session (NestJS,
  frontend, serverless, Python, …), apply its security rows too; it carries what is
  specific to one runtime.

Reviewing a single change set against its plan before merge is `reviewing-code`.
Auditing IaC, IAM, network or cloud configuration is `infrastructure-auditor`.

## Non-negotiable Rules

| Severity | Rule |
| --- | --- |
| MUST | Stay read-only. Report findings and remediation as code the reader can apply; never modify a file or mutate any state. Restrict shell use to read verbs and read-only scanners. |
| MUST | Run only the scanners the project **already has installed**. Never install a tool to audit with it. When no scanner is present for a surface, do a manual review and say a scan did not run — never present a code-only audit as though a scan confirmed it. |
| MUST | Apply the universal baseline classes as the floor; layer the project's own rules (which outrank it), a named standard when asked, and the installed stack skill's rows on top. |
| MUST | Triage every dependency advisory by reachability and exploitability before assigning severity. An advisory in a package the code never reaches on an exploitable path is not a blocker — say so and rank it accordingly. |
| MUST | Evidence every finding: a file and line, or a package and advisory id. Severity is consequence, not confidence; state confidence and what you could not check separately. |
| MUST | Name what was not checked — a surface you could not reach, an ecosystem with no scanner. A gap the reader does not know about is the most dangerous output of an audit. |
| NEVER | Pad the report. Consolidate repeats into one finding with the list. If a dimension is clean, say so in one line. No redesigns — the minimum correction only. |

## Reference Loading

| Reference | Load when | Covers |
| --- | --- | --- |
| [Dependency triage](./references/dependency-triage.md) | Triaging advisories, a lockfile change, or running an ecosystem audit | The read-only scanner command per ecosystem, the reachability → exploitability → severity → action model, and how to report when no scanner is installed |
| [Security review checklist](${CLAUDE_PLUGIN_ROOT}/skills/reviewing-code/references/security-review-checklist.md) | Mapping code findings to classes — every audit | The universal baseline class catalog, shared with `reviewing-code`: what each class is, what to look for, and the minimum correction |

## Procedure

Copy this checklist and track progress:

```text
Application security audit:
- [ ] 1. Scope and standard
- [ ] 2. Map the attack surface
- [ ] 3. Run the installed scanners
- [ ] 4. Map findings to the baseline classes
- [ ] 5. Triage dependencies
- [ ] 6. Rank and report
```

**Step 1 — Scope and standard.** Settle what is in scope (the whole service or a named
surface) and the bar (the baseline by default, or a standard the caller names). Read
the project's own security rules and conformance target; they outrank the baseline.

**Step 2 — Map the attack surface.** List the entry points — HTTP handlers, webhooks,
queue and event consumers, scheduled jobs, CLI — and for each, the trust boundary, the
authentication and authorization it applies, the data stores and outbound calls it
reaches, the secrets it uses, and where it deserializes or evaluates input. The surface
is what the audit walks; a missed entry point is a missed finding.

**Step 3 — Run the installed scanners.** Only what the project already has: a SAST
scanner (for example `semgrep`), a secret scanner (`gitleaks`, `trufflehog`), the
ecosystem dependency audit, and a filesystem/container scanner (`trivy fs`,
`osv-scanner`). Record the exact commands. If none is installed, say so and proceed by
manual review.

**Step 4 — Map findings to the baseline classes.** Walk the surface against the shared
class catalog, per entry point — broken access control and object-level authz first.
Apply the installed stack skill's security rows and any named standard. Each hit gets a
class, evidence, consequence, and the minimum correction.

**Step 5 — Triage dependencies.** Follow [dependency-triage](./references/dependency-triage.md):
reachability, then exploitability, then severity, then the action. An unreachable
advisory is recorded, not escalated.

**Step 6 — Rank and report.** Most severe first, evidence on every finding, the three
things to fix first, and an explicit list of what was not checked. Use the report shape
below.

## Report

```markdown
## Application Security Audit

### Scope and data sources
What was audited, against which bar, which scanners ran (verbatim), and what you could not reach.

### Summary
Counts by severity, and the three things to fix first.

### Findings
#### [SEVERITY] Short title
- **Where:** file:line, or package@version + advisory id
- **Class:** the baseline class (or the standard's control)
- **Consequence:** what happens if it stays
- **Correction:** the minimum change that removes the risk

### Dependencies
| Package@version | Advisory | Reachable? | Exploitable? | Severity | Action |

### Not checked
Surfaces out of reach, ecosystems with no scanner, and what it would take to cover them.
```

Where the audit is written for people outside the team, apply
`/tsh-core:writing-technical-documents` to it.

## Related Skills

Ships in this plugin — if this skill loaded, it is installed.

- [`reviewing-code`](../reviewing-code/SKILL.md) — the pre-merge review of a single
  change set; shares the baseline class catalog this audit applies across a surface.
- [`discovering-technical-context`](../discovering-technical-context/SKILL.md) —
  establishes the project conventions and security rules the audit judges against.
