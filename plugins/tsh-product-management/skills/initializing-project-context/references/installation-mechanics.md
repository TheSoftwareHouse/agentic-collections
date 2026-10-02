# Installation mechanics

Read before wiring repositories, when asked "why not install once in the catalog", or
when a session in a code repository cannot see the plugin. Verified on Claude Code
2.1.263, 2026-09-13, by experiment and against the documentation; the
`tsh-product-management` rows re-verified 2026-09-30.

## What was verified

| Fact | How |
| --- | --- |
| Project-scope settings apply only to the **folder the session starts in**. A `.claude/settings.json` in the catalog does **not** reach repositories below it: `claude plugin list` there shows the plugin `disabled`. | Installed at catalog scope; listed from `repo/`, `repo/sub/`, sibling. Docs: settings are read "from the session's primary working directory". |
| A `.claude/settings.json` inside `<repo>/` with the relative source `../<slug>-context` works: plugin `enabled`, skill visible in a real session started in `<repo>/`. | Wrote the file; `claude plugin list`; `claude -p` listed the plugin's skill. |
| Until the repository folder is **trusted** (the dialog at the first interactive session), its project settings are ignored, so the marketplace is not added and the plugin is not listed. | Untrusted `/tmp` repo: plugin absent, warning "this workspace has not been trusted". |
| `claude plugin marketplace add ../x --scope project` writes an **absolute** path — useless for teammates. | Observed `/private/tmp/…` in the written file. |
| A project `settings.json` declaring `tsh-agentic-collections` from GitHub does not disturb a machine that already registered it under that name from elsewhere: the existing registration wins, `tsh-product-management` stays `enabled`, and a session in a code repository ran `navigating-project-context` and resolved the context repository beside it. | `claude plugin marketplace list` unchanged; `claude plugin list`; `claude -p` from `<repo>/`. |
| A `CLAUDE.md` in the catalog **does** load in sessions below it. | Docs: files "in the directory hierarchy above the working directory are loaded at launch"; confirmed by quoting it from a child session. |

Consequences: the skill wires each repository with `wire_repos.py --register`
(CLI registration, then the relative path, existing keys preserved), and puts a
`CLAUDE.md` — not a `settings.json` — in the catalog.

## The entry per repository

```json
{
  "extraKnownMarketplaces": {
    "<slug>-context": { "source": { "source": "directory", "path": "../<slug>-context" } },
    "tsh-agentic-collections": { "source": { "source": "github", "repo": "TheSoftwareHouse/agentic-collections" } }
  },
  "enabledPlugins": {
    "<slug>-shared@<slug>-context": true,
    "tsh-product-management@tsh-agentic-collections": true
  }
}
```

The second pair is what brings the four knowledge-base skills to every role. It is only
ever added, never overwritten: a repository that already declares the company
marketplace, or has disabled the plugin, keeps its own entry.

A relative `directory` path resolves against the repository's main checkout, so it
holds from a git worktree too. On trusting the folder Claude Code adds the
marketplace with no separate prompt.

## "Out of the box" — two paths, one verified here

| Who | How the plugin becomes live | Status |
| --- | --- | --- |
| The person running the scaffold | `wire_repos.py --register` runs, inside **the context repository itself and each chosen code repository**, `claude plugin marketplace add <abs context dir> --scope project` and `claude plugin install <slug>-shared@<slug>-context --scope project`, then rewrites the stored absolute path to the portable one — `.` for the context repository, `../<slug>-context` for a code repository. Result: `claude plugin list` shows `enabled` and a session started there runs `navigating-project-context`, with no trust dialog and no restart. | **Verified** in a fresh, untrusted repository and in a context repository referring to itself with `.`. |
| A teammate cloning the repository | The committed `.claude/settings.json` declares the marketplace and the plugin; on accepting the trust dialog at their first interactive session Claude Code adds the marketplace "with no separate prompt" and enables the plugin. | **Documented**, not reproduced here: in a non-interactive `claude -p` run, a trusted-by-config folder did **not** auto-register the marketplace, so the auto-add appears to be an interactive-startup behaviour. Tell the team to expect the dialog once. |

`wire_repos.py` registers via the CLI rather than writing the cache by hand because
the cache layout (`~/.claude/plugins/known_marketplaces.json`,
`installed_plugins.json`) is Claude Code's own and changes between releases.

**A settings file alone is not enough on the machine that runs the scaffold.**
Verified: writing `extraKnownMarketplaces` and `enabledPlugins` by hand and then
running `claude plugin list` in that folder shows nothing — the marketplace is not
registered. The CLI step is what registers it. This is why the context repository is
always wired: a catalog with no code repositories would otherwise finish with a
correct scaffold and nothing installed, which reads as a failed setup.

## Without the sibling checkout

The source is a path. A machine without `../<slug>-context` gets a marketplace load
error at startup and no project skills. Serving the marketplace from a git URL would
remove that dependency; it is a **pending decision** of the user, together with git
initialisation. Do not switch the source or add `git init` on your own.

## Verifying

```shell
claude plugin list        # <slug>-shared@<slug>-context — Scope: project, Status: enabled
```

`disabled` → session started in the wrong folder, or the folder is not trusted yet.
Marketplace error → the sibling checkout is missing or misnamed.

## The closing report

Five sections, in this order, nothing else. Fill the placeholders from what actually
happened; drop nothing, even when a section is empty.

```markdown
## Created
<catalog path>; <n> files in <slug>-context; <slug>/CLAUDE.md; optional layers: <chosen or "none">; settings in <targets>; GUIDE.pdf via <renderer or "not rendered: reason">

## Skipped (already existed)
<files, or "nothing">

## Verified
check_links.py ✔ · check_tables.py ✔ · claude plugin validate marketplace ✔, plugin ✔ · claude plugin list in <slug>-context — <slug>-shared@<slug>-context enabled

## Try it now
**This session will not show the plugin — its skill list was loaded before the plugin existed. Open a new one:** `claude` here, or in `<slug>-context`, or in any wired code repository. Then: `/tsh-product-management:navigating-project-context` to read the knowledge base, `writing-project-knowledge` to add to it, `repairing-project-context-links` to repair references, `adding-project-context-workspace` to add a workspace. `<slug>-shared` is empty until the team adds a skill specific to this project. Teammates accept the trust dialog once on their first session.

## Pending decisions
Who initialises `<slug>-context` in git, and when — until then the checker scripts run by hand and there is no pre-push gate · Whether the marketplace later moves to a git URL instead of the sibling checkout · Whether owners marked `TBD` are assigned before the first real content lands · *(only when the catalog was created next to a repository)* When `<folder_name>/` moves into `<slug>/` — the skill does not move repositories, and until then that repository cannot be wired
```

The **Try it now** opening sentence and every **Pending decisions** item are binding —
three, or four when the catalog was created next to a repository: without the first, a
`/plugin list` in the current session reads as a failed setup; without the second, the
team inherits open questions without knowing it.
