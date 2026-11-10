# The security invariants skill

Load this in Step 3. The skill you write is layer three of the security model this
plugin applies: the universal baseline is the floor, the stack skill adds runtime
depth, and **the project's own rules outrank both**. Without a written list, those
rules reach a review only when the right person happens to be the reviewer.

## 1. What counts as an invariant

An invariant here is all three:

- **Specific to this project.** It names a boundary, a data class, a provider or a
  mechanism of this system — "only the v3 webhook signature is accepted", not
  "verify webhook signatures".
- **Checkable.** A reviewer can tell from a diff, or an auditor from the code, whether
  it still holds.
- **Consequential.** Breaking it causes a breach, a leak, a compliance failure or a
  cost — not a style problem.

Generic security advice fails the first test and stays out. The baseline that
`reviewing-code` and `auditing-application-security` load already covers it, and a
copy here only drifts from the original.

## 2. Sources

Every invariant cites one. In order of authority:

| Source | Note |
| --- | --- |
| Written client or contractual requirements in the repository | A security annex, a compliance target, a data-residency requirement |
| `CLAUDE.md` hard rules | Already binding; the skill turns them into review checks and cites their numbers |
| Decision records with status `Accepted` | Only `Accepted` binds. Cite the record; never cite a `Proposed`, `Rejected` or `Superseded` one as a rule |
| `SECURITY.md` or a security policy | Disclosure process is out of scope; technical rules are in |
| Guard scripts and CI checks that enforce a rule | A script that fails the build on a wildcard IAM action is the team writing the rule down |
| Remediation lists from a past penetration test | Each fixed finding is a regression to guard against |

## 3. Candidates found only in code

The code shows what is done today, not what must stay true. When a pattern is
consistent and security-relevant — a constant-time comparison on every signature, a
logger that redacts one field everywhere, one module as the only path to secrets —
propose it, with where you saw it:

> I see `<pattern>` in `<files>`. Is it a rule the team wants every change to keep?

Ask in one batch, not one question at a time. Write a candidate only on a yes, with
the source "confirmed with the team during capture, <date>". That source is final: a
later run keeps the invariant as it stands and never re-proposes or removes it for
lacking a file. A declined candidate goes in the report and nowhere else.

## 4. Open decisions

Unsettled questions are invariants too: a change must not settle them silently. List
the ones the repository records — a README "open items" section, `Proposed` decision
records — with their source.

## 5. Grouping

Group by boundary, in the order an attacker would meet them, and use only the groups
this project has: ingress and authentication, authorization, personal and sensitive
data, secrets, permissions and infrastructure, external calls and cost, storage and
retention, open decisions.

## 6. A repository attached to a project knowledge base

A `tsh:project-context` block in `CLAUDE.md` or `CLAUDE.local.md` means the
repository belongs to a project with a `<slug>-context` knowledge base. Two things
change.

**Decision records live there, not in the repository.** Read them through
`/tsh-product-management:navigating-project-context`, which every attached
repository enables and which finds the person's clone itself. Only `Accepted` records
bind; a record kept in the code repository is one about that repository's own
internals.

**Shared invariants go to the project's own plugin.** The knowledge base ships
`plugins/<slug>-shared`, and its README states the sharing rule: a skill needed by
more than one role or repository of the project lives there; one needed by a single
repository stays in that repository's `.claude/`; ties go to the code repository. So:

- Draft every invariant first. Then ask, in one batch, which of them hold for every
  repository of the project. With no answer available, keep all of them in the
  repository and say so in the report.
- Invariants that hold project-wide become `<slug>-security-invariants`, at
  `plugins/<slug>-shared/skills/<slug>-security-invariants/SKILL.md`, from the same
  template with the project as its subject. Markdown only: no `allowed-tools`, hooks
  or scripts, which that plugin's `scripts/check_plugin.py` refuses. Bump `version` in
  `plugins/<slug>-shared/.claude-plugin/plugin.json` and add a line to its
  `CHANGELOG.md` in the same change; without the bump no teammate receives it.
- Nothing is written into the person's own clone of the knowledge base: its sync
  needs a clean default branch. The change goes through the attached plugin's write
  flow — propose, create a branch and worktree, write and check there, commit, push,
  each step after the person's own yes — which `navigating-project-context` loads.
  Run the knowledge base's own checks from that worktree before the commit step.
- The repository's own skill keeps the repository-specific invariants and opens with
  one line naming the shared skill, so a review in this repository applies both. The
  `tsh:project-checks` block names both too.

## 7. Template

Fill every `<…>`, keep each invariant to one or two sentences, and keep the result
under ~100 lines.

```markdown
---
name: reviewing-security-invariants
description: "The security invariants specific to <project> — <three to five boundary names> — that every review, audit and change touching them must preserve. Use when changing <boundaries or paths>, or when a security review or audit runs on this repository; not for generic security checklists, which reviews already apply."
---

# Security invariants of <project>

These outrank generic security checklists. Treat a review as read-only unless asked
to fix. When a change touches an invariant, open its source.

## Invariants

- **<Boundary>:** <what must stay true, concretely>. Source: `<path>` (<section or record>).

## Open decisions

A change must not settle these silently: <decision> (source: `<path>`).

## Report

Findings first, by severity, each with file and line, the invariant it breaks and the
impact. Separate confirmed defects from questions. With no findings, name the
invariants that were checked.
```
