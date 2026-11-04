---
title: Initializing Project Context
sidebar_label: Initializing Project Context
sidebar_position: 20
description: Sets up a project's context repository (its knowledge base and Claude Code marketplace), connects code repositories to it, and publishes it to a git host only after asking.
sources:
  - plugins/tsh-product-management/skills/initializing-project-context/
  - plugins/tsh-product-management/shared/locating-project-context.md
  - plugins/tsh-product-management/shared/locate_project_context.py
  - plugins/tsh-product-management/hooks/guard-project-context-block.mjs
sources_hash: "91722a8ba7c5797457acb2f54395d8ab5e70b75bffea31fb211a91fddc5851cf"
---

# Initializing Project Context

**Plugin:** [TSH Product Management](/docs/plugins/tsh-product-management/)  
**Invoke:** `/tsh-product-management:initializing-project-context` (`disable-model-invocation: true`: it runs only when you invoke it)  
**Used by:** [Navigating Project Context](/docs/plugins/tsh-product-management/skills/navigating-project-context), [Writing Project Knowledge](/docs/plugins/tsh-product-management/skills/writing-project-knowledge), [Adding a Project-Context Workspace](/docs/plugins/tsh-product-management/skills/adding-project-context-workspace) and [Repairing Project-Context Links](/docs/plugins/tsh-product-management/skills/repairing-project-context-links) point to it through the shared locating guide: when a repository is not connected, or its `tsh:project-context` block is missing or changed, they tell the person to run this skill in _Attach repository_ mode.

Sets up a project's context repository, a `<slug>-context` knowledge base that is also a Claude Code marketplace, and connects code repositories to it. The scaffold copies data, never logic: the four knowledge-base skills ship in this plugin and find the knowledge base on their own, so only the four checker scripts are copied, because a pipeline must run them with no plugin installed.

## Modes

The skill opens with a `Mode` question unless the arguments already name the mode.

| Mode                  | What it does                                                                                                                                                                                                                                                             |
| --------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **New project**       | Scaffolds `<slug>-context/` and the project's marketplace, commits locally, then publishes to an **empty** repository on the git host only if the person says yes. Code repositories are optional: a lead may start alone.                                               |
| **Attach repository** | Connects a code repository to an existing project: the marketplace, both plugins and the `tsh:project-context` block, in commit or local mode. Also connects a repository added months later, and lets each teammate connect a client's repository on their own machine. |
| **Add URL**           | Gives a knowledge base started without a remote its URL and publishes it after asking. Offered only when the locator reports `SOURCE=inside` and an empty `URL`.                                                                                                         |

## What it covers

| Area                    | Coverage                                                                                                                                                                                                                                                                                                                                     |
| ----------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Knowledge base**      | Five project workspaces (baseline, architecture, product, delivery, quality), three layer workspaces (backend, frontend, design), one decisions folder, a glossary, two conventions (decisions and ownership), four checker scripts, a Bitbucket pipeline, and the root `README.md`, `CLAUDE.md` and `GUIDE.md`                              |
| **Optional layers**     | `Mobile` and `Platform` from templates, or any other layer as one kebab-case name; each gets a row in the area map. Baseline, architecture, product, delivery, quality, backend, frontend and design are always created and are not offered                                                                                                  |
| **Project marketplace** | `.claude-plugin/marketplace.json` and the plugin `<slug>-shared`, created **empty**: no skill, agent or hook, it is the slot for the project's own Markdown skills                                                                                                                                                                           |
| **Fixed questions**     | Asks only through AskUserQuestion, only the fixed calls in the question contract (`Mode`, `Project`, `Owner`, `Layout`, `Layers`, `Scaffold`, `Repos`, `Client`, `Remote`, `Push`, `URL`), with their headers, options and order. A turn never ends on a prose question                                                                      |
| **Probe first**         | Runs `probe.py` and builds the options from its output; name and owner are never derived by the skill. The git identity may be offered as an option, never used unpicked                                                                                                                                                                     |
| **Owners**              | Owner fields are the person the user picks, or the literal placeholder `TBD — assign an owner`. No invented owners, decisions or terms                                                                                                                                                                                                       |
| **Connection modes**    | Commit mode for a repository the team may commit config to; local mode for a client's repository or when there is no URL yet (see below)                                                                                                                                                                                                     |
| **Git boundary**        | Git commands that change state run only through `context_repo_git.py` (knowledge base) and `wire_repos.py` (`ls-remote` only). No commit, branch, push or config change in a code repository                                                                                                                                                 |
| **Publishing**          | One push only: the first push of a new knowledge base, after an explicit yes to the `Push` question in this run, to an empty remote. Never a force-push, never to a remote that already has branches; otherwise the commands are printed                                                                                                     |
| **Validation**          | `claude plugin validate` on the marketplace and the plugin, and the four checker scripts, all pass before the first local commit. A failure is a defect in the skill's templates: it is reported, not hand-patched                                                                                                                           |
| **No leakage**          | Nothing about any client, employer or other project reaches a generated file, including as an example                                                                                                                                                                                                                                        |
| **Pointer protection**  | The `tsh:project-context` block is written and replaced only by `wire_repos.py`, never edited by hand. A plugin hook denies an Edit or Write on `CLAUDE.md` or `CLAUDE.local.md` that would remove or change it. A shell command that rewrites the file (`sed -i`, `>`) is not caught; the next read reports the block as missing or changed |

## Commit mode and local mode

|                 | Commit mode: the team may commit config                    | Local mode: the client's repository, or no URL yet                       |
| --------------- | ---------------------------------------------------------- | ------------------------------------------------------------------------ |
| Settings file   | `.claude/settings.json`                                    | `.claude/settings.local.json`                                            |
| Project pointer | `tsh:project-context` block in `CLAUDE.md`                 | the same block in `CLAUDE.local.md`                                      |
| Kept out of git | `.claude/settings.local.json`                              | both files, through `.git/info/exclude`; never the client's `.gitignore` |
| Who commits     | the person, in a pull request; the skill never does        | nobody                                                                   |
| Teammates       | get it with the next pull and accept the trust dialog once | each runs _Attach repository_ once                                       |

Both modes add the project marketplace with `<slug>-shared`, and the company marketplace `tsh-agentic-collections` with `tsh-product-management`, so the four knowledge-base skills reach every role. The company pair is only ever added: an existing entry, including a `false`, is kept. `settings.local.json` also gets the person's own clone in `permissions.additionalDirectories`; that path exists on one machine, which is why it never goes into the committed file.

Without a URL the marketplace source is the clone's absolute path, and the repository is wired in local mode whatever was asked. _Add URL_ followed by _Attach repository_ moves it to the URL.

## How it works

1. **Probe and pick the mode.** `probe.py` and the locator run first, then the `Mode` question.
2. **New project.**
   1. Ask `Project`, `Owner`, `Layout` and `Layers`. The slug is never asked: it is the kebab-case of the name.
   2. Run `scaffold.py --dry-run`, show the file list, then ask `Scaffold`, `Repos`, `Client` and `Remote`.
   3. Scaffold for real and run the four checkers and both plugin validations from the new folder.
   4. Render `GUIDE.pdf`, wire the knowledge base itself (`--self`), and make the first commit locally.
   5. With a URL: check it and set it as `origin`, ask `Push`, and on yes push the first commit to the empty remote.
   6. Always run `wire_repos.py --self --register`, adding `--commit` for the team's own repositories and `--local` for a client's. `--register` makes the plugin live on this machine at once, in the knowledge base and in every wired repository. Confirm `<slug>-shared@<slug>-context` is enabled with `claude plugin list`.
3. **Attach repository.** Resolve the project's URL (a wired repository already has it; otherwise ask `URL`), resolve this person's clone, ask `Client` per repository, then wire it. A URL that `ls-remote` cannot reach, or a name this machine already uses for another project, stops with nothing written.
4. **Add URL.** Ask `URL`, set it as origin, ask `Push`. Afterwards, re-run _Attach repository_ in each connected code repository so its settings move from the local path to the URL.
5. **Report.** Five sections in this order: Created, Connected, Verified, Try it now, Still to do. Everything reported must have happened in this run, and the report states that the current session cannot see the new plugin: a new session is required.

Without a pushed URL every repository is wired in local mode, and the skill says so.

## Edge cases

| Situation                                                 | Behaviour                                                                                                                                                                                                                                                                                                                                                      |
| --------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Run inside a code repository                              | The current directory is a git repository, so the knowledge base cannot be created in it. The `Layout` options become _Next to this repository_, _In a new folder next to this repository_, or `Stop`. The skill never moves repositories                                                                                                                      |
| `!` overlap warning in the dry run                        | A custom layer that is a synonym of an existing workspace prints a `!` line, and that line is a question for the person, asked before the `Scaffold` call: drop the layer or keep it with a distinct scope. A layer with exactly the name of an always-created workspace is dropped by the script                                                              |
| Name taken (scaffold exit 3, or `wire_repos.py` refusing) | `<slug>-context` already belongs to another project on this machine: in the registry, at `~/.tsh/context/<slug>/`, or in Claude Code's marketplace list. For a new project the name is asked again; for _Attach repository_ the skill stops, because the project's lead must rename one of the two. The registry is never edited and no marketplace is removed |
| Remote refused: cannot reach                              | Wrong URL, repository not created yet, or credentials need a prompt. Continue without a URL and publish later with _Add URL_                                                                                                                                                                                                                                   |
| Remote refused: already has branches                      | Someone published a knowledge base there. Never push; clone it with _Attach repository_ instead                                                                                                                                                                                                                                                                |
| Remote refused: origin already set                        | Both URLs are reported and the skill stops; changing an existing origin is the person's call                                                                                                                                                                                                                                                                   |
| Attach with no access                                     | `wire_repos.py` runs `git ls-remote` before writing anything; a failure means the person needs access on the git host first. Nothing was written                                                                                                                                                                                                               |

## Installation mechanics

The skill's reference records these facts, verified on Claude Code 2.1.263 and 2.1.303:

- Project-scope settings apply only to the folder the session starts in, so each code repository carries its own.
- Until the folder is trusted, project settings are ignored: no marketplace, no plugin.
- Settings declarations register at the start of an interactive session. The person running init gets the plugin at once only through the CLI step (`--register`).
- A git-URL marketplace copies each plugin to `~/.claude/plugins/cache/`, only the plugin folder and never `docs/`.
- An update arrives only when `version` in `plugin.json` changes.
- A git worktree of a client repository does not have the local `settings.local.json` and `CLAUDE.local.md`; the locator still finds the project through the main checkout, but the project plugin and the pointer block are missing in that worktree's sessions.

## Scripts

| Script                | Role                                                                                                                                                                    |
| --------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `probe.py`            | Prints the values the fixed questions need as JSON (folder names, git owner, siblings, `can_be_catalog`, slugs). Writes nothing                                         |
| `scaffold.py`         | Creates the knowledge base from templates; never overwrites an existing file, reports every skip. Refuses a slug this machine already uses for another project (exit 3) |
| `render_guide_pdf.py` | Renders `GUIDE.md` to `GUIDE.pdf` with pandoc, or with headless Chrome or Chromium. Exit 3 means no renderer: the skill continues and quotes the manual command         |
| `context_repo_git.py` | The three git steps of a new knowledge base, each separate so the skill can ask between them: `init`, `remote`, `first-push --yes`                                      |
| `wire_repos.py`       | Connects code repositories: settings, the pointer block, the registry in `~/.tsh/context/`, and with `--register` the `claude` CLI registration                         |

## Related skills

- [Navigating Project Context](/docs/plugins/tsh-product-management/skills/navigating-project-context), [Writing Project Knowledge](/docs/plugins/tsh-product-management/skills/writing-project-knowledge), [Adding a Project-Context Workspace](/docs/plugins/tsh-product-management/skills/adding-project-context-workspace) and [Repairing Project-Context Links](/docs/plugins/tsh-product-management/skills/repairing-project-context-links): the four knowledge-base skills this scaffold relies on instead of copying.
- [Managing Decision Records](/docs/plugins/tsh-core/skills/managing-decision-records): owns the decision-record format; the scaffold has no decision-record skill and `conventions/decisions.md` matches it.
- [Managing Claude Context](/docs/plugins/tsh-core/skills/managing-claude-context): with `tsh-core` installed, owns the knowledge base's `CLAUDE.md` and the workspace `CLAUDE.md` files after the scaffold.

## Source

- [`SKILL.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-product-management/skills/initializing-project-context/SKILL.md)
- References: [question contract](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-product-management/skills/initializing-project-context/references/question-contract.md), [edge cases](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-product-management/skills/initializing-project-context/references/edge-cases.md), [installation mechanics](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-product-management/skills/initializing-project-context/references/installation-mechanics.md)
- Scripts: [`probe.py`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-product-management/skills/initializing-project-context/scripts/probe.py), [`scaffold.py`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-product-management/skills/initializing-project-context/scripts/scaffold.py), [`render_guide_pdf.py`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-product-management/skills/initializing-project-context/scripts/render_guide_pdf.py), [`context_repo_git.py`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-product-management/skills/initializing-project-context/scripts/context_repo_git.py), [`wire_repos.py`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-product-management/skills/initializing-project-context/scripts/wire_repos.py)
- Shared: [`locating-project-context.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-product-management/shared/locating-project-context.md), [`locate_project_context.py`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-product-management/shared/locate_project_context.py)
- Hook: [`guard-project-context-block.mjs`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-product-management/hooks/guard-project-context-block.mjs)
