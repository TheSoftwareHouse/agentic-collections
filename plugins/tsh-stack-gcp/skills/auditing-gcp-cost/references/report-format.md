# GCP cost audit report format

The report is the deliverable. Save the file **before** presenting results, without
asking for confirmation, then state the full path on one line and summarize.

Filename:

```text
gcp-cost-audit-<project>-<region>-YYYY-MM-DD.md
```

For example `gcp-cost-audit-my-project-us-central1-2026-03-05.md`.

Follow the structure below exactly rather than improvising — these reports are read
side by side across accounts and across months, and a re-ordered section defeats
that.

The structure is fixed; the prose inside it is not. Apply
`/tsh-core:writing-technical-documents` to the executive summary and the finding
descriptions — these go to people who will not read past the first section.

## Structure

````text
# GCP Cost Optimization Audit
**Project:** `<project-id>`   **Region:** `<region>`   **Date:** YYYY-MM-DD
**Data Sources:** IaC (Terraform) / Live API / Both
**Scope:** All services / <specific services>

---

## 📋 Executive Summary

- <bullet 1>
- <bullet 2>
- ... (3–6 bullets max)

---

## 🔍 IaC vs Live Infrastructure Drift

| # | Resource | IaC State | Live State | Drift Type |
|---|---|---|---|---|
| 1 | `instance-prod-01` | `e2-standard-4` | `e2-standard-8` | Config drift |
| 2 | `fw-allow-ssh` | Not in IaC | Active | Shadow resource |

*(If no IaC was found, or no drift detected, state that clearly.)*

---

## 💰 Optimization Opportunities

| # | Resource ID | Type | Current Config | Current Cost ($/mo) | Recommended Config | Est. New Cost ($/mo) | Savings ($/mo) | Path |
|---|---|---|---|---|---|---|---|---|
| 1 | `instance-prod-01` | Compute Engine | `e2-standard-4` | $140 | `e2-standard-2` | $70 | **$70** | 🟢 Golden |
| 2 | `db-prod-01` | Cloud SQL | `db-custom-8-32768, 500 GB pd-ssd` | $820 | `db-custom-4-16384, 500 GB pd-balanced` | $510 | **$310** | 🔵 Cost-Opt |

> Path legend: 🟢 Golden Path · 🔵 Cost-Optimized · 🚀 Velocity

---

## 🏷️ Label Compliance

| # | Resource ID | Type | Missing Tags | Status |
|---|---|---|---|---|
| 1 | `instance-prod-01` | Compute Engine | `owner`, `data_class` | ❌ FAIL |
| 2 | `my-bucket` | Cloud Storage | — | ✅ PASS |

---

## 🔒 Critical Security Findings

| # | Resource ID | Type | Finding | Severity |
|---|---|---|---|---|
| 1 | `fw-allow-ssh` | Firewall Rule | Port 22 open to 0.0.0.0/0 | 🔴 HIGH |

*(If none found, write: "No critical security findings detected.")*

---

## 📊 Summary

| Metric | Value |
|---|---|
| Total current monthly spend | $X,XXX |
| Total estimated optimized spend | $X,XXX |
| **Total estimated savings** | **$X,XXX/mo (XX%)** |
| Label compliance | XX% (X of Y resources fully labelled) |
| IaC coverage | XX% (X of Y resources managed by IaC) |
| Drift detected | X resources with configuration drift |
| Data sources used | GCP API / Terraform code / Both |

---

## ✅ Recommended Action Order

1. Apply optimization #X — highest savings, lowest risk
2. ...
````

## Formatting rules

- `---` horizontal rule between every major section.
- Section icons exactly as shown: 📋 🔍 💰 🏷️ 🔒 📊 ✅.
- `❌ FAIL` / `✅ PASS` in the label compliance status column — not bold text alone.
- Path legend exactly as shown: 🟢 Golden · 🔵 Cost-Opt · 🚀 Velocity.
- Resource IDs always in backticks.
- Left-aligned table columns — `|---|`, never `|:---:|`.
- No extra prose paragraphs between tables.
- Where cost is estimated rather than read from the BigQuery billing export, say so in
  the executive summary. Do not mark an estimate as measured spend.

## After presenting

Ask exactly one follow-up question:

> Would you like me to generate Terraform code to implement these optimizations?

- **No** → the workflow ends; the saved report stands alone.
- **Yes** → ask which opportunity numbers to apply (`1, 3, 5` or `all`) and modify
  only those. If no infrastructure code exists in the workspace, ask for a path or
  repository URL, then discover its conventions before writing anything. Show a diff
  preview before writing to any existing file.

Never generate or modify code before the user names the specific items.
