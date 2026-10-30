---
name: initializing-project-context
description: "Sets up a project's context repository — a knowledge base with named owners per project and delivery layer, one folder for all decision records, a quality gate, and a Claude Code marketplace for the project's own Markdown skills — as a local git repository it can publish to Bitbucket, GitHub or any git host after asking; connects code repositories to it, committed for the team's own repositories and local-only for a client's; and publishes a knowledge base started without a remote. Run /tsh-product-management:initializing-project-context in the folder where the project should live, or in a code repository to connect."
disable-model-invocation: true
---

# Initializing project context

Target: **$ARGUMENTS**

Three modes:

- **New project** — scaffolds `<slug>-context/`: the knowledge base (five project
  workspaces, three layer workspaces, one decisions folder, a glossary, two
  conventions, four checker scripts, a Bitbucket pipeline) and the project's Claude Code
  marketplace with the plugin `<slug>-shared`, created **empty**. Commits it locally,
  then — only if the person says yes — publishes it to an **empty** repository on the
  git host. Code repositories are optional: a lead may start alone.
- **Attach repository** — connects a code repository to an existing project: the
  marketplace, both plugins and the `tsh:project-context` block, in commit or local mode.
  The same mode connects a repository added months later, and lets each teammate
  connect a client's repository on their own machine.
- **Add URL** — gives a knowledge base started without a remote its URL, and publishes
  it after asking.

**The scaffold copies data, never logic.** The four knowledge-base skills ship in this
plugin and find the knowledge base on their own; only the checker scripts are copied,
because a pipeline must run them with no plugin installed.

## Explicit Exclusions

- No commit, branch, push or config change in a **code** repository. Files are written
  there; the person commits them (commit mode) or git never sees them (local mode).
- No push except the first push of a new knowledge base, after an explicit yes, to an
  empty remote. Never a force-push, never to a remote that already has branches.
- Nothing written outside the new `<slug>-context/`, the code repositories the person
  selected, and the per-person registry in `~/.tsh/context/`.
- No invented owners, decisions or terms. Owner fields are the person the user picks,
  or the literal placeholder `TBD — assign an owner`.
- No skill, agent or hook in the generated plugin. It is the slot for the project's own
  Markdown skills; anything every project needs the same way belongs in this marketplace.
- No decision-record skill in the scaffold — `/tsh-core:managing-decision-records` owns
  that format and `conventions/decisions.md` matches it.
- **Nothing about any client, employer or other project** reaches a generated file.

## Non-negotiable Rules

| Severity | Rule |
| --- | --- |
| MUST | Ask **only** through AskUserQuestion, **only** the fixed calls in [the question contract](./references/question-contract.md), with its headers, questions, options and order. Context changes option labels, never the shape. A turn never ends on a prose question. |
| MUST | Run `probe.py` first and build the options from its output. Never derive name or owner yourself; offering the git identity as an option is fine, using it unpicked is not. |
| MUST | Run git only through `context_repo_git.py` (knowledge base) and `wire_repos.py` (`ls-remote` only). No other git command that changes state. |
| NEVER | Push without the person's yes to the `Push` question in this run. Without it, print the commands instead. |
| MUST | Ask, for every code repository, whether it is the client's. A client's repository is wired in **local** mode; nothing is committed or staged there. |
| NEVER | Overwrite an existing file. `scaffold.py` skips them; report every skip. |
| MUST | Run `claude plugin validate` on the generated marketplace and plugin, and the four checker scripts from `CONTEXT_DIR`, before committing. All must pass. |
| NEVER | Put a client name, an employer name or another project's details into a generated file, including as an example. |
| NEVER | Edit the `tsh:project-context` block by hand. `wire_repos.py` writes and replaces it. |
| MUST | State in the report that the **current session cannot see the new plugin** and a new session is needed. |

## Reference Loading

| Reference | Load when | Covers |
| --- | --- | --- |
| [Question contract](./references/question-contract.md) | Before every AskUserQuestion call | Every fixed call: headers, questions, options, when a question is skipped |
| [Edge cases](./references/edge-cases.md) | `can_be_catalog` is false, the dry run prints a `!` line, or a remote is refused | Placement inside a code repository, overlap warnings, a non-empty or unreachable remote |
| [Installation mechanics](./references/installation-mechanics.md) | Before wiring, and at the report | Commit and local mode in detail, trust, what teammates do, the closing report's exact wording |

## Procedure

**Step 1 — Probe and pick the mode.** Run `python3 ${CLAUDE_SKILL_DIR}/scripts/probe.py`
and `python3 ${CLAUDE_PLUGIN_ROOT}/shared/locate_project_context.py`, then make call
**M** (`Mode`). Skip it when `$ARGUMENTS` names the mode.

### New project

**N1 — Questions.** Call **N1** (`Project`, `Owner`, `Layout`, `Layers`). The slug is
never asked: kebab-case of the name, or the probe's `folder_slug` / `parent_slug` when
an existing folder receives the knowledge base.

**N2 — Dry run.** Run

```shell
python3 ${CLAUDE_SKILL_DIR}/scripts/scaffold.py --name "<name>" --slug <slug> \
  --owner-name "<name>" --owner-email <email> --layers <chosen…> <placement> --dry-run
```

(`--owner-tbd` for *Assign later*; no `--layers` for *None*; `<placement>` per the
`Layout` answer, as in the question contract). A `!` line is a question first, and
exit 3 means the name is taken on this machine — see
[edge cases](./references/edge-cases.md). Show the file list, then call **N2**
(`Scaffold`, `Repos`, `Client`, `Remote`).

**N3 — Scaffold, validate, commit locally.** The same command without `--dry-run`;
capture `CONTEXT_DIR` and `SLUG`. From `CONTEXT_DIR` all must pass:

```shell
python3 scripts/check_links.py && python3 scripts/check_tables.py && python3 scripts/check_decisions.py && python3 scripts/check_plugin.py
claude plugin validate . && claude plugin validate plugins/<slug>-shared
```

A failure is a defect in this skill's templates: report it, do not hand-patch. Then,
in this order, so the first commit carries the knowledge base's own settings and the
guide for readers who will not open Markdown:

```shell
python3 ${CLAUDE_SKILL_DIR}/scripts/render_guide_pdf.py "<CONTEXT_DIR>"
python3 ${CLAUDE_SKILL_DIR}/scripts/wire_repos.py --kb "<CONTEXT_DIR>" --slug <slug> --self
python3 ${CLAUDE_SKILL_DIR}/scripts/context_repo_git.py init "<CONTEXT_DIR>"
```

`render_guide_pdf.py` exit 3 means no renderer: continue, and quote the manual command it
printed in the report.

**N4 — Remote, only with a URL.** When `Remote` carried a URL:
`python3 ${CLAUDE_SKILL_DIR}/scripts/context_repo_git.py remote "<CONTEXT_DIR>" <URL>`.
Refused → [edge cases](./references/edge-cases.md) §"Remote refused"; continue without a
URL. Accepted → call **P** (`Push`). On `Push`:
`python3 ${CLAUDE_SKILL_DIR}/scripts/context_repo_git.py first-push "<CONTEXT_DIR>" --yes`.
Otherwise, and for *Show me how*, print the commands from
[installation mechanics](./references/installation-mechanics.md) §"Publishing by hand".

**N5 — Wire.** Read [installation mechanics](./references/installation-mechanics.md), then
always:

```shell
python3 ${CLAUDE_SKILL_DIR}/scripts/wire_repos.py --kb "<CONTEXT_DIR>" --slug <slug> \
  [--url <URL, only if pushed>] --self --register --commit <own repos…> --local <client repos…>
```

Without a pushed URL every repository is wired in local mode; say so. Confirm with
`claude plugin list` inside `CONTEXT_DIR` that `<slug>-shared@<slug>-context` is enabled.

### Attach repository

**A1 — The project.** From the locator: a wired repository already has the URL — say so,
and re-running repairs the settings and the block. Otherwise call **A1** (`URL`). Then
resolve this person's clone with
`python3 ${CLAUDE_PLUGIN_ROOT}/shared/locate_project_context.py --url <URL>`, following
`${CLAUDE_PLUGIN_ROOT}/shared/locating-project-context.md` for exit 3.

**A2 — The repository.** Call **A2** (`Client`) for the current repository, or each
selected one. Then run `python3 ${CLAUDE_SKILL_DIR}/scripts/wire_repos.py --kb <KB> --slug
<SLUG> --url <URL> --register` with `--commit` or `--local`. A URL `ls-remote` cannot
reach, or a name this machine already uses for another project, stops here with nothing
written — see [edge cases](./references/edge-cases.md).

### Add URL

**U1.** The knowledge base is the session's folder (locator `SOURCE=inside`) with no
remote. Call **A1** (`URL`), then N4. After the push, re-run *Attach repository* in each
connected code repository, so its settings move from the local path to the URL.

**Last step — Report.** The sections and their exact wording are in
[installation mechanics](./references/installation-mechanics.md) §"The closing report".
Everything reported must have happened in this run.

## Self-check Before Handoff

```text
- [ ] Only the fixed AskUserQuestion calls, with their headers, questions and option shapes
- [ ] Name and owner were picked or typed by the user; nothing inferred
- [ ] Git ran only through context_repo_git.py and wire_repos.py; nothing committed in a code repository
- [ ] Pushed only after a yes in this run, and only to an empty remote; otherwise commands printed
- [ ] Every code repository was asked about; client repositories are in local mode
- [ ] All four checker scripts and both validations passed before the local commit
- [ ] No generated file names a client, an employer or another project
- [ ] The generated plugin holds no skill; the knowledge-base skills were not copied
- [ ] The report says a new session is required, and lists what the person still has to commit or push
```
