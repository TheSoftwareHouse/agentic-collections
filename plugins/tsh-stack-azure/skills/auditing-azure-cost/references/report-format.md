# Azure cost audit report format

The report is the deliverable. Save the file **before** presenting results, without
asking for confirmation, then state the full path on one line and summarize.

Filename:

```text
azure-cost-audit-<subscription>-<region>-YYYY-MM-DD.md
```

For example `azure-cost-audit-prod-westeurope-2026-04-02.md`.

Follow the structure below exactly rather than improvising — these reports are read
side by side across accounts and across months, and a re-ordered section defeats
that.

The structure is fixed; the prose inside it is not. Apply
`/tsh-core:writing-technical-documents` to the executive summary and the finding
descriptions — these go to people who will not read past the first section.

## Structure

````text
# Azure Cost Optimization Audit
**Subscription:** `<name or id>`   **Region:** `<region>`   **Date:** YYYY-MM-DD
**Data Sources:** IaC (Terraform / Bicep) / Live API / Both
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
| 1 | `vm-prod-01` | `Standard_D4s_v5` | `Standard_D8s_v5` | Config drift |
| 2 | `nsg-allow-rdp` | Not in IaC | Active | Shadow resource |

*(If no IaC was found, or no drift detected, state that clearly.)*

---

## 💰 Optimization Opportunities

| # | Resource ID | Type | Current Config | Current Cost ($/mo) | Recommended Config | Est. New Cost ($/mo) | Savings ($/mo) | Path |
|---|---|---|---|---|---|---|---|---|
| 1 | `vm-prod-01` | Virtual Machine | `Standard_D4s_v5` | $140 | `Standard_D2s_v5` | $70 | **$70** | 🟢 Golden |
| 2 | `sql-prod-01` | SQL Database | `GP_Gen5_8, GRS` | $820 | `GP_Gen5_4, LRS` | $430 | **$390** | 🔵 Cost-Opt |

> Path legend: 🟢 Golden Path · 🔵 Cost-Optimized · 🚀 Velocity

---

## 🏷️ Tag Compliance

| # | Resource ID | Type | Missing Tags | Status |
|---|---|---|---|---|
| 1 | `vm-prod-01` | Virtual Machine | `Owner`, `DataClass` | ❌ FAIL |
| 2 | `stprodassets` | Storage Account | — | ✅ PASS |

---

## 🔒 Critical Security Findings

| # | Resource ID | Type | Finding | Severity |
|---|---|---|---|---|
| 1 | `nsg-allow-rdp` | NSG | Port 3389 open to Internet | 🔴 HIGH |

*(If none found, write: "No critical security findings detected.")*

---

## 📊 Summary

| Metric | Value |
|---|---|
| Total current monthly spend | $X,XXX |
| Total estimated optimized spend | $X,XXX |
| **Total estimated savings** | **$X,XXX/mo (XX%)** |
| Tag compliance | XX% (X of Y resources fully tagged) |
| IaC coverage | XX% (X of Y resources managed by IaC) |
| Reservation / savings-plan utilization | XX% |
| Hybrid Benefit applied | X of Y eligible Windows/SQL resources |
| Drift detected | X resources with configuration drift |
| Data sources used | Azure API / IaC / Both |

---

## ✅ Recommended Action Order

1. Apply optimization #X — highest savings, lowest risk
2. ...
````

## Formatting rules

- `---` horizontal rule between every major section.
- Section icons exactly as shown: 📋 🔍 💰 🏷️ 🔒 📊 ✅.
- `❌ FAIL` / `✅ PASS` in the tag compliance status column — not bold text alone.
- Path legend exactly as shown: 🟢 Golden · 🔵 Cost-Opt · 🚀 Velocity.
- Resource IDs always in backticks.
- Left-aligned table columns — `|---|`, never `|:---:|`.
- No extra prose paragraphs between tables.
- Where cost is estimated rather than read from Cost Management, say so in the executive
  summary. Do not mark an estimate as measured spend.

## After presenting

Ask exactly one follow-up question:

> Would you like me to generate Terraform code to implement these optimizations?

- **No** → the workflow ends; the saved report stands alone.
- **Yes** → ask which opportunity numbers to apply (`1, 3, 5` or `all`) and modify
  only those. If no infrastructure code exists in the workspace, ask for a path or
  repository URL, then discover its conventions before writing anything. Show a diff
  preview before writing to any existing file.

Never generate or modify code before the user names the specific items.
