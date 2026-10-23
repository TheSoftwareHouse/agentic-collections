# Installation mechanics

Read before wiring repositories, when a session in a code repository cannot see the
plugin, and when writing the closing report. Verified on Claude Code 2.1.263
(2026-09-13) and 2.1.303 (2026-10-23), by experiment against a local git host and
against the documentation.

## What was verified

| Fact | How |
| --- | --- |
| Project-scope settings apply only to the folder the session starts in; each code repository carries its own. | Installed at a parent folder's scope; `claude plugin list` from a child showed `disabled`. |
| Until the folder is **trusted** (the dialog at the first interactive session), project settings are ignored — no marketplace, no plugin. | Untrusted repository: plugin absent, warning "this workspace has not been trusted". |
| Settings declarations register at the start of an **interactive** session; `claude -p` does not register them. The person running init gets the plugin at once only through the CLI step (`--register`). | Hand-written settings + `claude plugin list` showed nothing until the CLI step. |
| A git-URL marketplace copies each plugin to `~/.claude/plugins/cache/<marketplace>/<plugin>/<version>/` — only the plugin folder, never `docs/`. | Inspected the cache after install from a local git host. |
| An update arrives only when `version` in `plugin.json` changes. A commit to `docs/` only, or a skill change without a bump, delivers nothing. | `plugin update` → "already at the latest version" in both cases; delivered after a bump. |
| Adding a marketplace of the same name from another source **replaces** the source; installed plugins update from the new one, no reinstall. | `marketplace add` with a folder, then a git URL. |
| Reading a folder outside the session's folder prompts for permission, unless it is in `permissions.additionalDirectories`. | `claude -p` refused; allowed after the entry in `settings.local.json`. |
| `CLAUDE.local.md` loads like `CLAUDE.md`, and git does not ignore it by itself. | A session quoted it; `git status` listed it as untracked. |
| A plugin hook with `if: "Edit(**/CLAUDE.md)"` starts only for that file; other edits never spawn it. | Logged invocations across edits of several files. |

## Commit mode and local mode

| | Commit mode — a repository the team may commit config to | Local mode — the client's repository, or no URL yet |
| --- | --- | --- |
| Settings file | `.claude/settings.json` | `.claude/settings.local.json` |
| Project pointer | `tsh:project-context` block in `CLAUDE.md` | the same block in `CLAUDE.local.md` |
| Kept out of git | `.claude/settings.local.json` (read access) | both files, in `.git/info/exclude` — never the client's `.gitignore` |
| Who commits | the person, in a pull request; the skill never does | nobody, ever |
| Teammates | get it with the next pull, accept the trust dialog once | each runs *Attach repository* once |

The settings entry:

```json
{
  "extraKnownMarketplaces": {
    "<slug>-context": { "source": { "source": "git", "url": "<URL>", "sparsePaths": [".claude-plugin", "plugins"] } },
    "tsh-agentic-collections": { "source": { "source": "github", "repo": "TheSoftwareHouse/agentic-collections" } }
  },
  "enabledPlugins": {
    "<slug>-shared@<slug>-context": true,
    "tsh-product-management@tsh-agentic-collections": true
  }
}
```

The company pair brings the four knowledge-base skills to every role. It is only ever
added: an existing entry, including a `false`, is kept. `settings.local.json`
additionally gets `permissions.additionalDirectories: ["<this person's clone>"]` — a
path on one machine, which is why it is never in the committed file.

Without a URL the source is the clone's absolute path, and the repository is wired in
local mode whatever was asked: a committed path would be wrong on every other machine.
*Add URL* followed by *Attach repository* moves it to the URL.

A local `settings.local.json` and `CLAUDE.local.md` exist only in the checkout they were
written in. A git worktree of a client repository does not have them; the locator still
finds the project through the main checkout, but the project plugin and the pointer
block are missing in that worktree's sessions.

## Publishing by hand

When the person keeps the push for themselves, print exactly:

```shell
# 1. Create an EMPTY repository named <slug>-context on the git host
#    (no README, no .gitignore — the first push must land in an empty repository).
# 2. Then, in <CONTEXT_DIR>:
git remote add origin <URL>
git push -u origin main
# 3. Protect the default branch on the host: no direct pushes, one approval.
# 4. Connect code repositories: /tsh-product-management:initializing-project-context → Attach repository.
```

## The closing report

Five sections, in this order, nothing else. Fill the placeholders from what actually
happened; drop nothing, even when a section is empty.

```markdown
## Created
<CONTEXT_DIR>; <n> files; optional layers: <chosen or "none">; first commit <sha> on main; GUIDE.pdf via <renderer or "not rendered: reason">

## Connected
<repo> — commit mode: write the two files listed, to commit in a pull request · <repo> — local mode: nothing to commit · or "no code repositories yet — connect them later with Attach repository"

## Verified
check_links ✔ · check_tables ✔ · check_decisions ✔ · check_plugin ✔ · claude plugin validate marketplace ✔, plugin ✔ · claude plugin list in <slug>-context — <slug>-shared@<slug>-context enabled

## Try it now
**This session will not show the plugin — its skill list was loaded before the plugin existed. Open a new one** in `<slug>-context` or in a connected repository. Then `/tsh-product-management:navigating-project-context`. Teammates accept the trust dialog once on their first session; for a client's repository each runs *Attach repository* once.

## Still to do
<Only what applies:> Publish: <pushed to URL | "not published — only you can see it; Add URL when the empty repository exists" | the printed commands> · Commit the commit-mode files in each connected repository · Protect the default branch on the git host · Assign owners marked TBD before the first real content lands
```

The **Try it now** opening sentence is binding: without it, a `/plugin list` in the
current session reads as a failed setup. **Still to do** names everything the person
must do by hand, because the skill deliberately did not.
