---
title: Auditing Application Security
sidebar_label: auditing-application-security
sidebar_position: 0
description: A security audit of a whole service or a named surface — maps the attack surface, runs only the scanners the project already has, applies the universal baseline plus any named standard, and triages dependency advisories by reachability before severity.
sources:
  - plugins/tsh-product-engineering/skills/auditing-application-security/
  - plugins/tsh-product-engineering/agents/security-auditor.md
sources_hash: "29501615eede36d7428d5f855bd4c43f98d74a1a6f1749a38cefc6613b4e090d"
---

# Auditing Application Security

**Plugin:** [`tsh-product-engineering`](/docs/plugins/tsh-product-engineering/)  
**Invoke:** `/tsh-product-engineering:auditing-application-security`  
**Used by:** the [`security-auditor`](/docs/plugins/tsh-product-engineering/agents/security-auditor) agent preloads it.

A review reads a change; an audit reads a **surface**. The job is an accurate, prioritized picture of where a service is exposed, that someone can act on: the whole codebase or a named part of it, not one diff. The skill reports findings and never fixes code.

Use it for a security audit, a security posture review, an OWASP Top 10 or ASVS assessment, pen-test preparation, "how exposed are we", or triaging the output of a SAST scanner, an ecosystem dependency audit, Dependabot or a CVE advisory. Reviewing a single change set before merge is [`reviewing-code`](/docs/plugins/tsh-product-engineering/skills/reviewing-code). Auditing IaC, IAM, network or cloud configuration is [`@tsh-platform-engineering:infrastructure-auditor`](/docs/plugins/tsh-platform-engineering/agents/infrastructure-auditor).

## What sets the bar

| Layer | Role |
| :-- | :-- |
| **Universal baseline** | The floor. The class catalog is `reviewing-code`'s security-review checklist, applied here across a whole surface instead of a single change |
| **Project rules** | A client ruleset, a `SECURITY.md`, a project security-invariant skill (named in `CLAUDE.md`'s `tsh:project-checks` block or in the skill listing), or a stated conformance target outranks the skill and is applied first |
| **Named standard** | On request, OWASP Top 10 in full, ASVS L1/L2 or pen-test preparation extends the baseline, and the report says which. With nothing named, the baseline is the bar |
| **Stack depth** | Where a stack skill is available in the session, its security rows apply on top |

## Key rules

| Area | Coverage |
| :-- | :-- |
| **Read-only** | Remediation goes in the report as code the reader can apply. Shell use is restricted to read verbs and read-only scanners |
| **Installed scanners only** | It never installs a tool to audit with it. When no scanner is present for a surface, it reviews manually and says a scan did not run, never presenting a code-only audit as though a scan confirmed it |
| **Dependency triage** | Every advisory is triaged by reachability and exploitability before it gets a severity. An advisory in a package the code never reaches on an exploitable path is not a blocker |
| **Evidence** | Every finding has a file and line, or a package and advisory id. Severity is consequence, not confidence; confidence and what could not be checked are stated separately |
| **Named gaps** | What was not checked, such as an unreachable surface or an ecosystem with no scanner, is listed explicitly |
| **No padding** | Repeats are consolidated into one finding, a clean dimension gets one line, and the correction is the minimum one, never a redesign |

## How it works

1. **Scope and standard:** the whole service or a named surface, and the bar, reading the project's own security rules first.
2. **Map the attack surface:** every entry point (HTTP handlers, webhooks, queue and event consumers, scheduled jobs, CLI), with its trust boundary, authentication and authorization, data stores and outbound calls, secrets, and where it deserializes or evaluates input.
3. **Run the installed scanners:** a SAST scanner such as `semgrep`, a secret scanner (`gitleaks`, `trufflehog`), the ecosystem dependency audit, and a filesystem scanner (`trivy fs`, `osv-scanner`), recording the exact commands.
4. **Map findings to the baseline classes** per entry point, broken access control and object-level authorization first, plus the stack skill's rows and any named standard.
5. **Triage dependencies:** reachability, then exploitability, then severity, then the action.
6. **Rank and report:** most severe first, the three things to fix first, and an explicit list of what was not checked.

The report has fixed sections: scope and data sources, a summary with counts by severity, findings with location, class, consequence and correction, a dependency table (package, advisory, reachable, exploitable, severity, action), and Not checked.

## Reference Loading

| Reference | Load when |
| :-- | :-- |
| `dependency-triage.md` | Triaging advisories, a lockfile change, or running an ecosystem audit |
| `reviewing-code`'s `security-review-checklist.md` | Mapping code findings to classes, every audit |

`dependency-triage.md` carries the read-only audit command per ecosystem and the reachability → exploitability → severity → action model.

## Related skills

- [`reviewing-code`](/docs/plugins/tsh-product-engineering/skills/reviewing-code) is the pre-merge review of a single change set and shares the baseline class catalog this audit applies across a surface.
- [`discovering-technical-context`](/docs/plugins/tsh-product-engineering/skills/discovering-technical-context) establishes the project conventions and security rules the audit judges against.

## Source

[`plugins/tsh-product-engineering/skills/auditing-application-security/SKILL.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-product-engineering/skills/auditing-application-security/SKILL.md)
