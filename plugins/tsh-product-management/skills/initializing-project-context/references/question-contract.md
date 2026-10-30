# Question contract

Every question this skill asks, as fixed AskUserQuestion calls. One call per row group,
questions in the order shown. A question that leads to a change names where it lands —
the folder, the repository or URL — and whether it stays on this machine. Context changes option labels, never the shape. Skip a
question only when `$ARGUMENTS` already answers it unambiguously.

## M — the mode

| Header | Question | Options (label — description) |
| --- | --- | --- |
| `Mode` | What do you want to set up? | `New project` — Create the project's knowledge base and its shared plugin · `Attach repository` — Connect a code repository to an existing project's knowledge base · `Add URL` — Publish a knowledge base that was started without a git host. Offer `Add URL` only when the locator printed `SOURCE=inside` and an empty `URL`. |

## N1 — the new project

| # | Header | Question | Options (label — description) |
| --- | --- | --- | --- |
| 1 | `Project` | What is the project called? | `<name_option_a>` — From this folder's name · `<name_option_b>` — From the parent folder's name. Any other name via *Other*. Say that the name must be unique in the company — client and project, e.g. "Acme Shop", not "Shop": it names the repository on the git host and the project's plugin, and two projects of one name collide on every machine that has both. |
| 2 | `Owner` | Who owns the context repository? | `<git_owner>` — From your git config · `Assign later` — Every owner field reads "TBD — assign an owner". When `git_owner` is null the first option is `Type "Full Name (e-mail)" via Other`. |
| 3 | `Layout` | Where should `<slug>-context` be created? | When `can_be_catalog` is true: `In this folder` — `<folder_name>/<slug>-context`, beside the repositories already here · `In a new folder <slug>/ here` — a project folder that will hold the knowledge base and later the code repositories. When it is **false**, the options are in [edge cases](./edge-cases.md) §"Inside a code repository". Either way, say that teammates may keep their clone anywhere — the layout is the person's choice, not a contract. |
| 4 | `Layers` | Which extra layer workspaces does this project need? *(multi-select)* | `Mobile` — mobile applications: platform targets, release process, device constraints · `Platform` — infrastructure and pipelines: environments, provisioning, CI/CD, observability, secrets · `None` — neither for now. Any other layer through *Other* as one kebab-case name. Baseline, architecture, product, delivery, quality, backend, frontend and design are always created and are **not** offered — name them in the question text, and say that synonyms (`qa`, `infra`, `ui`) belong in the workspace that exists. |

`<placement>` for the scaffold: `In this folder` → `--catalog-dir "$PWD" --slug <slug>`;
`In a new folder <slug>/ here` → `--parent "$PWD"`; `Next to this repository` →
`--catalog-dir ".." --slug <slug>`; `In a new folder <slug>/ next to this repository` →
`--parent ".."`.

## N2 — create, connect, publish

| # | Header | Question | Options |
| --- | --- | --- | --- |
| 1 | `Scaffold` | Create these files in `<CONTEXT_DIR>` and commit them there? Nothing leaves this machine. | `Create` — Write the files listed above and make the first commit; nothing is pushed · `Stop` — Write nothing |
| 2 | `Repos` *(only when git repositories sit beside it)* | Which repositories should be connected to the knowledge base? *(multi-select)* | Each git repository from `siblings` (or `parent_siblings`), at most three, plus `None`. Description: "settings, the project pointer in CLAUDE.md, and read access for you". |
| 3 | `Client` *(only with `Repos`)* | Which of them belong to the client — nothing may be committed there? *(multi-select)* | The same repositories, plus `None — all are ours`. Description of each: "local mode: config stays on this machine, git ignores it; each teammate connects it themselves". |
| 4 | `Remote` | Where will `<slug>-context` live on the git host? | `Keep it local for now` — Only you see it; publish later with *Add URL* · `Show me how` — Print how to create an empty repository and push. The URL of an **empty** repository you created on Bitbucket, GitHub or another host comes through *Other*, SSH or HTTPS. |

## P — the push

| Header | Question | Options |
| --- | --- | --- |
| `Push` | Push `<branch>` of `<CONTEXT_DIR>` to the empty repository `<URL>` now? | `Push` — Publish it; from now on every change goes through branches and pull requests · `I'll push myself` — Print the command and leave it to you |

Never asked without a reachable, empty remote. Never assumed from an earlier answer.

## A1 — the project's URL

| Header | Question | Options |
| --- | --- | --- |
| `URL` | What is the URL of the project's context repository? | One option per registry entry of this machine (`<slug> — <url>`), at most three; the URL through *Other*. For a lead working alone, a registry entry with an empty URL is offered as `<slug> — local only, at <path>`. |

## A2 — the repository's owner

| Header | Question | Options |
| --- | --- | --- |
| `Client` | May the team commit Claude Code configuration to `<repo>`? | `Yes — our repository` — `.claude/settings.json` and a `CLAUDE.md` block, for you to commit in a pull request · `No — the client's` — local mode: `settings.local.json` and `CLAUDE.local.md`, ignored by git; each teammate connects it themselves |

One question per repository, up to four in one call.
