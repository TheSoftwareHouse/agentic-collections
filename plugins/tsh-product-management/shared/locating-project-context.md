# Locating the project's knowledge base

Every project-context skill in this plugin starts here. The plugin is enabled in the
context repository, in the project catalog and in each code repository beside it, and
the knowledge base sits somewhere different relative to each, so resolve it before
reading anything:

```shell
python3 ${CLAUDE_PLUGIN_ROOT}/shared/locate_project_context.py
```

It prints `KB=<path>` and `SLUG=<slug>`. Build every later path from **KB** —
`KB/docs/`, `KB/docs/decisions/README.md`, `KB/conventions/` — and use **SLUG** where a
skill names the project's own plugin, `<SLUG>-shared`.

| Exit | Means | Do |
| --- | --- | --- |
| 0 | Found | Continue with KB |
| 1 | No context repository from here upward | Stop. Say the knowledge base is not checked out beside this repository, and that a checkout of `<project>-context` belongs in the project catalog. Do not answer project questions from memory in the meantime. |
| 2 | Several in one folder | Ask which project the task belongs to, from the printed candidates. Never pick one. |

## Where a decision record goes

**`KB/docs/decisions/` — always, whichever folder the session started in.** One
folder, one number sequence, one index, for the whole project. A record written into a
code repository is the failure this rule exists to prevent, and it is the easy mistake,
because a tool writing records defaults to the repository it was started in.

Write one with **`/tsh-core:managing-decision-records`**, giving it `KB/docs/decisions/`
as the archive location. That skill owns the format, the statuses, numbering and the
index sync; `KB/conventions/decisions.md` says where the records live and what the
`Scope` column holds. Never write the record yourself when that skill is available, and
never set a status.

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
