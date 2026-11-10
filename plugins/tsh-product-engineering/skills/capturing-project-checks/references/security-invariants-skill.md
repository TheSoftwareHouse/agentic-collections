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
lacking a file. A declined candidate goes in the report and in one HTML comment at
the end of the generated skill (`<!-- declined during capture: … -->`), so a later
run does not ask again.

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

A `tsh:project-context` block in `CLAUDE.md` or `CLAUDE.local.md`, read from disk,
or an enabled `<slug>-shared@<slug>-context` plugin in the repository's settings,
means the repository belongs to a project with a `<slug>-context` knowledge base. This skill
only reads that knowledge base. It writes nothing there and runs no git there: the
knowledge base has its own write process and owners, and its sync needs a clean
clone.

**Decision records live there, not in the repository.** Read them through
`/tsh-product-management:navigating-project-context`, which finds the person's clone
itself. When that skill is not in this session — disabled, an untrusted folder, a
non-interactive run — say so, report the decision records as not read, and write no
invariant that would have needed one. Only `Accepted` records bind. Cite a record by
number and title, prefixed "knowledge base:", never by a path: the path does not
exist in this repository.

**Every invariant stays in the repository's skill.** Nothing is moved out, so a
review never applies fewer invariants than before the run.

**Project-wide invariants are marked, and drafted for the shared plugin.** The
knowledge base ships `plugins/<slug>-shared`, whose README states the sharing rule: a
skill needed by more than one role or repository of the project lives there; one
needed by a single repository stays in that repository's `.claude/`; ties go to the
code repository.

- Ask, in one batch, which invariants hold for more than one repository of the
  project. Mark each confirmed one `(project-wide)` after its name; the mark is how a
  later run knows the answer. With no answer, mark none.
- Put a draft of `<slug>-security-invariants` in the report, from the template below
  with the project as its subject and only the marked invariants. Cite each source by
  repository name and rule, or by record number and title: the plugin installs
  without the knowledge base's documents, so a path there resolves to nothing.
- With the draft, give the person the steps from that plugin's README, "Adding a
  component": the file is
  `plugins/<slug>-shared/skills/<slug>-security-invariants/SKILL.md`, Markdown only;
  `version` in `plugins/<slug>-shared/.claude-plugin/plugin.json` is bumped and
  `CHANGELOG.md` gets a line in the same pull request; the knowledge base's own
  `scripts/check_plugin.py`, at its root, checks all three in the pipeline. The
  person, or the knowledge base's owners, make that change.
- Once `<slug>-security-invariants` appears in a session's skill listing, a later run
  may replace the marked invariants in the repository's skill with one line naming
  it. Never before.

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
