# Edge cases

Situations the first run in an empty folder never meets. They change what the person is
asked, never the shape of the fixed calls.

## Inside a code repository

`can_be_catalog` is false: the current directory is a git repository, and creating the
knowledge base here would nest one repository inside another. Replace the two `Layout`
options with these, saying why in the question:

- `Next to this repository` — `<parent_name>/<slug>-context`, beside this repository.
  Only when `parent_is_git_repo` is false and `parent_writable` is true.
- `In a new folder <slug>/ next to this repository` — a new project folder in
  `<parent_name>/`. This repository stays where it is; the skill never moves
  repositories, and it does not need to — the connection is by URL, not by path. Only
  when `parent_writable` is true.
- `Stop` — always, and alone when neither option qualifies.

Offer to connect this repository in `Repos`: it is the obvious first one.

## Overlap warnings

**A `!` overlap warning in the dry run is a question for the person, not a note.** It
means a custom layer names, or is a synonym of, a workspace every project already gets.
Quote it, say which existing workspace covers the topic, and ask whether to drop the
layer or keep it with a distinct scope — before call N2, in prose. Two folders on one
topic split the knowledge, and the routing skill then has two plausible destinations
for the same document.

## Name taken

**Scaffold exit 3, or `wire_repos.py` refusing with "already names another project"**:
on this machine `<slug>-context` already belongs to another project — in the registry,
at `~/.tsh/context/<slug>/`, or in Claude Code's marketplace list. Two projects of one
name would share one marketplace, one plugin and one clone, so each would get the
other's knowledge and skills. Quote where it is taken. For *New project*, ask `Project`
again for a different name, then repeat the dry run; nothing was written. For *Attach
repository*, stop: the project's lead must rename one of the two projects. Never edit
the registry or remove a marketplace to make room.

## Remote refused

`context_repo_git.py remote` refuses in three cases. Quote its message, then:

| Refusal | Means | Do |
| --- | --- | --- |
| Cannot reach | Wrong URL, the repository does not exist yet, or credentials need a prompt | Say which of the three is likely from the message. Continue without a URL — the knowledge base is committed locally and *Add URL* publishes it later |
| Already has branches | Someone published a knowledge base there | Never push. Say that this project already has one: clone it (*Attach repository* with that URL) instead of the new scaffold, and that the local scaffold can be deleted |
| origin is already set | The knowledge base points somewhere else | Report both URLs and stop. Changing an existing origin is the person's call, by hand |

## Attach repository with no access

`wire_repos.py` runs `git ls-remote` before writing anything. A failure means this
person cannot read the context repository: they need access on the git host (or a
working SSH key / credential helper) first. Nothing was written; re-run afterwards.
