# Locating the project's knowledge base

Every project-context skill in this plugin starts here. The knowledge base (**KB**) is a
clone of the project's `<slug>-context` repository, and it can sit anywhere: beside the
code, in a project folder, or in `~/.tsh/context/<slug>/`. Resolve it, then bring it up
to date, before reading anything.

**PLUGIN** below is the folder above `shared/` in the path you read this file from. Write
it out in full in every command: `${CLAUDE_PLUGIN_ROOT}` is not set in the shell.

## 1. Locate

```shell
python3 PLUGIN/shared/locate_project_context.py            # from the session's folder
python3 PLUGIN/shared/locate_project_context.py --url <URL> # no code repository: by URL
```

It prints `KEY=VALUE` lines. Build every later path from **KB** — `KB/docs/`,
`KB/docs/decisions/README.md`, `KB/conventions/` — and use **SLUG** where a skill names
the project's own plugin, `<SLUG>-shared`.

| Exit | Means | Do |
| --- | --- | --- |
| 0 | Found | Continue with KB, then check `BLOCK` and `READ_ACCESS` below |
| 1 | Not wired, nothing found | Stop. Say this repository is not connected to a project knowledge base, and that `/tsh-product-management:initializing-project-context` connects it (*attach repository*), or that `--url <URL>` reads a known project from anywhere. Do not answer project questions from memory. |
| 2 | Several in one folder (old layout) | Ask which project the task belongs to, from the candidates on stderr. Never pick one. |
| 3 | Wired, but this person has not chosen a clone yet | Ask **once**, with AskUserQuestion: header `Knowledge`, question "Where should the `<SLUG>` knowledge base live on this machine?", options — each `CANDIDATE` first (`Use <path>` — an existing clone of this project), then `Clone to <DEFAULT>` (recommended when there is no candidate), then `Other folder` (the person types a path). Then re-run with `--use <path>` or `--clone <path>`. The choice is remembered for every repository of the project. |
| 4 | `--use` / `--clone` refused | Show the message. A path that is another project's clone is never used. |

`--clone` needs read access to the repository on the git host; a failure names the
cause (no SSH key loaded, no credential helper for HTTPS). Never retry with a different
URL or protocol on your own.

**`BLOCK=missing` or `BLOCK=drift`** — the `tsh:project-context` block in this
repository's `CLAUDE.md` (or `CLAUDE.local.md` in local mode) is gone or points at
another URL. Say so in one line and offer to restore it through
`/tsh-product-management:initializing-project-context` (*attach repository*). Never
restore or edit it yourself.

**`READ_ACCESS=missing`** — sessions in this repository will be asked for permission
each time they read KB, because it is outside the folder. Offer once: "Allow sessions in
this repository to read the knowledge base?" On yes, re-run with `--grant-read` — it
writes only to `.claude/settings.local.json`, which stays out of git. On no, carry on;
reads will prompt.

## 2. Sync

```shell
python3 PLUGIN/shared/sync_project_context.py "<KB>"
```

It prints JSON. The only change it can make is a fast-forward of a clean clone that is
on the default branch. **Put every entry of `warnings` at the top of your answer**, one
line each, in the reader's language — they say what the answer is based on: a branch
instead of the approved version, uncommitted changes, an offline or out-of-date copy,
a knowledge base nobody else can see yet.

On `diverged` the server's history was rewritten and the clone cannot follow it. Offer,
with AskUserQuestion (header `Fresh copy`): "Make a fresh copy of the knowledge base in
`<KB>-fresh`? The current one stays as it is." On yes, run §1 with `--clone
"<KB>-fresh"` — the new copy is used from then on; the old one is never deleted, say
that the person may remove it. On no, keep reading the old one with the warning.

## 3. Writing — three questions, three answers

Every change to the knowledge base goes through these steps. **Each git step runs only
after its own yes; one yes never covers another step.**

1. **Propose.** `python3 PLUGIN/shared/write_worktree.py start "<KB>" docs/<topic>`
   changes nothing and prints `WORKTREE`, `BRANCH`, `BASE`, `BASE_COMMIT`, `UPSTREAM`.
2. **Ask `Create`.** AskUserQuestion, header `Create`: "Create branch `<BRANCH>` from
   `<BASE>` (the remote's default) at `<BASE_COMMIT>`, in `<WORKTREE>`? Your own copy
   stays untouched." Options `Create` / `Cancel`. On `Create`:
   `python3 PLUGIN/shared/write_worktree.py start "<KB>" <BRANCH> --yes --at <BASE_COMMIT>`.
   Call `WORKTREE` **W**; read and write only under W.
3. **Write and check** under W, as the calling skill says.
4. **Show, then ask `Commit`.** Show the change in the reader's terms: each file with one
   line on what changed, and the diff (`git -C "<W>" diff` and new files) when asked.
   AskUserQuestion, header `Commit`: "Commit this change on `<BRANCH>`?" Options
   `Commit` / `Change something` / `Cancel`. On `Commit`:
   `python3 PLUGIN/shared/write_worktree.py commit "<W>" --message "<message>" --yes`.
5. **Ask `Push`.** AskUserQuestion, header `Push`: "Push `<BRANCH>` to `<UPSTREAM>` for
   review? Base `<BASE>` at `<BASE_COMMIT>`." Options `Push` / `Keep local`. On `Push`:
   `python3 PLUGIN/shared/write_worktree.py push "<W>" --yes`. The person opens the pull
   request from the link it prints.

On `Cancel` or `Keep local`, stop and say where the work is: W and its branch stay on
this machine, untouched, for the person to finish or delete. Never delete them yourself.

| Step and exit | Do |
| --- | --- |
| `start`, 1 | Stop: the remote could not be asked (offline, no access). Say so. **Never** fall back to writing in KB. |
| `start` (proposal), 2 | The name is taken or unusable: propose `docs/<topic>-2` and ask `Create` again. |
| `start --yes`, 4 | The proposal no longer holds (the remote moved, the name was taken meanwhile): propose again and ask `Create` again. |
| `start`, 3 | No remote yet: the exception below. |
| `commit` or `push`, 1 or 2 | Show the message and stop. Never retry differently, never force, never commit or push by hand. |

**The one exception: no remote yet.** The knowledge base exists only on this machine (a
lead starting alone) and there is nothing to branch from. Only if KB has no uncommitted
changes, ask with AskUserQuestion, header `Write`: "This knowledge base has no remote
yet. Write the change directly in `<KB>`?" Options `Write here` / `Cancel`. On yes,
write in KB, then step 4 with `commit "<KB>"`. Say that the change exists only on this
machine until the project gets its URL.

## Git rules — every project-context skill

| Operation | Allowed |
| --- | --- |
| `fetch`, `pull --ff-only` on a clean default branch | Only through `sync_project_context.py` |
| `clone` | Only through `--clone`, after the person chose the folder |
| Creating a branch and worktree, committing, pushing | Only through `write_worktree.py`, each after its own yes (§3) |
| Opening the pull request | The person does it; give them the link or the command |
| Push to the default branch, merge, rebase, stash, reset, checkout in the person's clone, force-push, deleting a branch or a worktree | **Never** |

## Where a decision record goes

**`KB/docs/decisions/` — always, whichever folder the session started in.** One
folder, one number sequence, one index, for the whole project. A record written into a
code repository is the failure this rule exists to prevent, and it is the easy mistake,
because a tool writing records defaults to the repository it was started in.

Write one with **`/tsh-core:managing-decision-records`**, giving it `W/docs/decisions/`
as the archive location. That skill owns the format, the statuses, numbering and the
index sync; `KB/conventions/decisions.md` says where the records live and what the
`Scope` column holds. Never write the record yourself when that skill is available,
and never set a status.

A record about one code repository's own internal conventions may stay in that
repository. Anything another repository or another role would need to know goes to KB.

## What binds, wherever you read from

- `KB/CLAUDE.md` and the owning workspace's `CLAUDE.md` outrank the skill that sent you
  here. They are the project's rules; the skill is the procedure.
- Only decision records with status `Accepted` are constraints. A `Superseded` record
  is read together with its successor, never alone.
- A document carrying a `DEPRECATED` banner under its title is history, not current
  state. Check for it before citing anything.
- Each workspace's `CLAUDE.md` names its owner. That person reviews changes there.
