---
title: Security Auditor
sidebar_label: security-auditor
sidebar_position: 2.5
description: Audits an application's code and dependencies for security across a whole service or a named surface, read-only, and returns a severity-ranked findings report.
sources:
  - plugins/tsh-product-engineering/agents/security-auditor.md
sources_hash: "affeedfa7f9c49d62e4c4d17e258f67154a6da2b2539db7e01a0a31b622f14bd"
---

# Security Auditor

**Plugin:** [`tsh-product-engineering`](/docs/plugins/tsh-product-engineering/)  
**Mention:** `@tsh-product-engineering:security-auditor`  
**Model:** `opus`  
**Tools:** no `tools` list in the frontmatter; `disallowedTools: Write, Edit`  
**Skills preloaded:** [`auditing-application-security`](/docs/plugins/tsh-product-engineering/skills/auditing-application-security), [`discovering-technical-context`](/docs/plugins/tsh-product-engineering/skills/discovering-technical-context)

Audits application security and reports findings. It does not fix anything, does not change any file and never mutates state. Its value is an accurate, prioritized picture of where the service is exposed, that someone can act on. Use it for a security audit, a posture review, an OWASP or ASVS assessment, pen-test preparation, or triaging scanner and CVE output. It is not for reviewing a single change before merge.

## Inputs it expects

The delegation should name the scope (the whole service or a named surface) and the bar: the universal baseline, or a standard such as OWASP Top 10 in full, ASVS L1/L2 or pen-test preparation. Defaults when unspecified:

- **Scope:** the current workspace, every entry point it exposes.
- **Bar:** the universal baseline, plus the installed stack skill's security rows.
- **Depth:** exhaustive rather than sampled.

A project's own security rules, such as a `SECURITY.md`, a client ruleset, a project security-invariant skill (named in `CLAUDE.md`'s `tsh:project-checks` block or in the skill listing) or a stated conformance target, outrank the baseline. It applies them first and says it did.

## Responsibilities

- Follows the `auditing-application-security` skill in full: settles scope and the bar, maps the attack surface entry point by entry point, runs the installed scanners, maps code findings to the universal baseline classes, applies any named standard, triages dependencies by reachability and exploitability, then ranks and reports.
- Restricts itself to read verbs and read-only scanners: `semgrep`, `gitleaks`, `trufflehog`, the ecosystem dependency audit (`npm audit`, `pnpm audit`, `pip-audit`, `composer audit`, `govulncheck`, `cargo audit`), `osv-scanner` and `trivy fs`. It runs only the scanners the project already has installed and never installs one.
- When no scanner is installed for a surface, says so and proceeds by manual review, never presenting a code-only audit as though a scan confirmed it.
- When the service targets a framework or stack whose skill is available in the session, loads it and applies its framework-specific security rows alongside the baseline. It loads whichever are present and never names one that is absent.

## What it returns

The report shape the skill defines:

1. **Scope and data sources:** which scanners ran, verbatim, and what it could not reach.
2. **Summary:** counts by severity and the three things to fix first.
3. **Findings,** most severe first, each with evidence (a file and line, or a package@version and advisory id) and the minimum correction. Repeats are consolidated.
4. **Dependencies:** the triaged advisory table.
5. **Not checked:** surfaces it did not reach and ecosystems it could not scan, the audit's most important caveat.

Severity is consequence, not confidence; confidence and gaps are stated separately. A clean dimension is reported in one line.

## Used by

No skill delegates to it. Mention it directly when you want the audit run by a read-only delegate rather than inline.

## Source

[`plugins/tsh-product-engineering/agents/security-auditor.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-product-engineering/agents/security-auditor.md)
