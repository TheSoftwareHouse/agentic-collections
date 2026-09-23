---
name: initializing-project-context
description: "Scaffolds a project's context repository — a knowledge base with named owners per project and delivery layer, one folder for all decision records, a link-and-table quality gate, and the Claude Code marketplace shipping four project-prefixed skills over it — then enables that plugin in the sibling code repositories and writes a guide for technical and non-technical readers. Run /tsh-product-management:initializing-project-context in the folder where the project should live."
disable-model-invocation: true
---

# Initializing project context

Target: **$ARGUMENTS**

Creates a **project catalog** `<slug>/` holding `<slug>-context/`, which is both the
project's knowledge base (plain markdown: five project workspaces, three layer
workspaces, one decisions folder, a glossary, two conventions, two checker scripts)
and its Claude Code marketplace — the plugin `<slug>-shared` with four skills,
`<slug>-context`, `<slug>-knowledge`, `<slug>-links`, `<slug>-space`. Code
repositories beside it enable that plugin from their own committed settings.

**Every generated skill name carries the project slug**, because with two projects
installed two skills called `project-context` are indistinguishable in the `/` menu.

## Explicit Exclusions

- **No git, anywhere.** No `init`, commit, remote or push; who initialises the
  repository is an open decision. The scaffold is plain files.
- No git-URL marketplace source; the source is the sibling checkout `../<slug>-context`.
- Nothing written outside `<slug>/` except the `.claude/settings.json` of code
  repositories the user selects.
- No invented owners, decisions or terms. Owner fields are the person the user picks,
  or the literal placeholder `TBD — assign an owner`.
- No decision-record skill in the generated plugin — `/tsh-core:managing-decision-records`
  owns that format and `conventions/decisions.md` matches it; a second copy would drift.
  The generated files route that skill to `<slug>-context/docs/decisions/` from every
  folder, so records never land in a code repository.
- **Nothing about any client, employer or other project** reaches a generated file.

## Non-negotiable Rules

| Severity | Rule |
| --- | --- |
| MUST | Ask **only** through the AskUserQuestion tool, **only** the two fixed calls below, with the exact headers, questions, options and order. Context changes option labels, never the shape. A turn never ends on a prose question. |
| MUST | Run `probe.py` first and build the options from its output. Never derive name or owner yourself; offering the git identity as an option is fine, using it unpicked is not. |
| NEVER | Run a git command that changes state. |
| NEVER | Overwrite an existing file. `scaffold.py` skips them; report every skip. |
| MUST | Always run Step 5, even with no code repositories. `wire_repos.py --register` wires the context repository and the catalog folder first, which is what makes the plugin usable straight after the scaffold. Never call the `claude plugin` CLI by hand. |
| MUST | Run `claude plugin validate` on the generated marketplace and plugin, and both checker scripts from `CONTEXT_DIR`, before reporting. All four must pass. |
| NEVER | Put a client name, an employer name or another project's details into a generated file, including as an example. |
| MUST | Treat a missing PDF renderer as a reported gap. `GUIDE.md` is the deliverable. |
| MUST | State in the report that the **current session cannot see the new plugin** and a new session is needed. Its skill list was built at startup; a `/plugin list` run here will not show it, which reads as a failed setup. |

## Reference Loading

| Reference | Load when | Covers |
| --- | --- | --- |
| [Installation mechanics](./references/installation-mechanics.md) | Before Step 5, and again at Step 7 | Verified facts about project-scope settings and trust, the per-repository entry, what "out of the box" means, the missing-checkout trade-off, and the closing report's exact wording |

## Procedure

**Step 1 — Probe, then the first fixed call.** Run
`python3 ${CLAUDE_SKILL_DIR}/scripts/probe.py` and read its JSON. Then make **one**
AskUserQuestion call with exactly these three questions:

| # | Header | Question | Options (label — description) |
| --- | --- | --- | --- |
| 1 | `Project` | What is the project called? | `<name_option_a>` — From this folder's name · `<name_option_b>` — From the parent folder's name. Any other name via *Other*. |
| 2 | `Owner` | Who owns the context repository? | `<git_owner>` — From your git config · `Assign later` — Every owner field reads "TBD — assign an owner". When `git_owner` is null the first option is `Type "Full Name (e-mail)" via Other`. |
| 3 | `Layout` | Where should the catalog live? | When `can_be_catalog` is true: `This folder is the catalog` — `<folder_name>` becomes the catalog; the context repository is created inside it, beside any code repositories already there · `Create <slug>/ here` — a new folder inside `<cwd>` named after the project. When it is **false**, the options are the ones under *Inside a code repository* below. |
| 4 | `Layers` | Which extra layer workspaces does this project need? *(multi-select)* | `Mobile` — mobile applications: platform targets, release process, device constraints · `Platform` — infrastructure and pipelines: environments, provisioning, CI/CD, observability, secrets · `None` — neither for now. Any other layer comes in through *Other* as one kebab-case name (`data-pipelines`, `integrations`) and gets a workspace from the generic template. Baseline, architecture, product, delivery, quality, backend, frontend and design are always created and are **not** offered here — name them in the question text, and say that synonyms of them (`qa` for quality, `infra` for platform, `ui` for frontend) belong in the workspace that exists, not in a second one. |

Skip a question only when `$ARGUMENTS` already answers it unambiguously. The slug is
never asked: it is the kebab-case of the name, or the probe's `folder_slug` (or
`parent_slug`) when an existing folder is the catalog — that folder keeps its own name;
the slug only names `<slug>-context` inside it. It is shown in Step 2 before anything is
written.

A layer left out costs nothing: `/<slug>-shared:<slug>-space` adds it later. An
unowned empty folder does cost something, which is why they are not all created.

**Inside a code repository** — `can_be_catalog` is false: the current directory is a git
repository, and `Create <slug>/ here` would nest the project inside one of its own
repositories. Replace the two `Layout` options with these, saying why in the question:

- `Parent folder is the catalog` — `<parent_name>/` becomes the catalog; the context
  repository lands beside this repository. First, and only when `parent_is_git_repo` is
  false and `parent_writable` is true. Its description must warn: right when the parent
  holds only this project's repositories, wrong for a general `projects/` folder, whose
  every session would load the catalog `CLAUDE.md`.
- `Create <slug>/ next to this repository` — a new catalog in `<parent_name>/`; this
  repository stays put, and the skill never moves it, so **Pending decisions** gains a
  fourth item: move `<folder_name>/` into `<slug>/`, then re-run Step 5. Only when
  `parent_writable` is true.
- `Stop` — always, and alone when neither parent option qualifies.

**Step 2 — Dry run, then the second fixed call.** Run

```shell
python3 ${CLAUDE_SKILL_DIR}/scripts/scaffold.py --name "<name>" --slug <slug> \
  --owner-name "<name>" --owner-email <email> \
  --layers <chosen…> <placement> --dry-run
```

Use `--owner-tbd` instead of the two owner flags when `Assign later` was chosen, and
omit `--layers` entirely when `None` was.

**A `!` overlap warning in the output is a question for the user, not a note.** It means
a custom layer names, or is a synonym of, a workspace every project already gets. Quote
it, say which existing workspace covers the topic, and ask whether to drop the layer or
keep it with a distinct scope — before the `Scaffold` call below, in prose. Two folders
on one topic split the knowledge, and the routing skill then has two plausible
destinations for the same document.

`<placement>` follows the `Layout` answer: `--catalog-dir "$PWD" --slug <folder_slug>`
for *This folder is the catalog*; `--parent "$PWD"` for *Create `<slug>/` here*;
`--catalog-dir ".." --slug <parent_slug>` for *Parent folder is the catalog*;
`--parent ".."` for *Create `<slug>/` next to this repository*. Show the file list (and
skips, if any), then make **one** AskUserQuestion call:

| # | Header | Question | Options |
| --- | --- | --- | --- |
| 1 | `Scaffold` | Create these files? | `Create` — Write the files listed above · `Stop` — Write nothing |
| 2 | `Repos` (only when the catalog already contains other folders) | Which repositories should enable the shared plugin? *(multi-select)* | Each folder name from `siblings` — from `parent_siblings` when the parent folder is the catalog — except `<slug>-context`, at most three, plus `None`. Not asked when the catalog was created next to this repository: it holds nothing yet. |

**Step 3 — Scaffold.** Same command without `--dry-run`. Capture `CONTEXT_DIR` and
`SLUG` from the last two lines.

**Step 4 — Validate.** From `CONTEXT_DIR`, all four must pass:

```shell
python3 scripts/check_links.py && python3 scripts/check_tables.py
claude plugin validate . && claude plugin validate plugins/<slug>-shared
```

A failure is a defect in this skill's templates: report it, do not hand-patch the
generated files.

**Step 5 — Make the plugin live.** Read
[`installation-mechanics.md`](./references/installation-mechanics.md), then run this
**always**, with `--only` carrying the repositories chosen in Step 2 if there were any:

```shell
python3 ${CLAUDE_SKILL_DIR}/scripts/wire_repos.py --catalog "<catalog>" --slug <slug> --register [--only <chosen…>]
```

It wires the context repository (source `.`) and the catalog folder (source
`./<slug>-context`) before any code repository, preserving existing settings keys.
Then confirm with `claude plugin list` inside `CONTEXT_DIR` that
`<slug>-shared@<slug>-context` is `enabled`, and put that line in the report.

**Step 6 — Render the guide.**
`python3 ${CLAUDE_SKILL_DIR}/scripts/render_guide_pdf.py "<CONTEXT_DIR>"`. Exit 0
writes `GUIDE.pdf`; exit 3 means no renderer — quote the manual command it printed.

**Step 7 — Report.** Five sections, in this order, and nothing more: **Created**,
**Skipped (already existed)**, **Verified**, **Try it now**, **Pending decisions**.
The exact wording of each is in
[`installation-mechanics.md`](./references/installation-mechanics.md) §"The closing
report" — read it before writing. Two parts are binding: **Try it now** opens with the
fact that this session cannot see the plugin and a new one is needed, and **Pending
decisions** lists all three unresolved — four when the catalog was created next to
this repository. Everything reported must have happened in this run.

## Self-check Before Handoff

```text
- [ ] Exactly two AskUserQuestion calls with the fixed headers, questions and option shapes
- [ ] Name and owner were picked or typed by the user; nothing inferred
- [ ] No git command changed state; no existing file overwritten
- [ ] The catalog is not inside a git repository; a session started in one used the parent
- [ ] Both checker scripts and both validations passed, and the report says so
- [ ] No generated file names a client, an employer or another project
- [ ] Step 5 ran; context repository and catalog are wired, `claude plugin list` confirmed it; only user-selected code repositories were added
- [ ] The report says a new session is required before the plugin appears
- [ ] GUIDE.md exists; the PDF outcome is stated
- [ ] The report has the five sections, including the pending decisions
```
