# Local mode and re-runs

Load this in Step 1 when the repository is attached in local mode, and in Step 4 on
every run: the pointer block's record line is how a later run knows what the team
already answered.

## 1. Local mode

A repository attached in local mode (the `tsh:project-context` block is in
`CLAUDE.local.md` and the plugin entry in `.claude/settings.local.json`) is one the
team may not commit to, usually a client's. Wiring already asked, and local mode is
the recorded "no": do not ask again. This skill adds no tracked file and changes none.

- **Resolve the exclude file first**, with `git rev-parse --git-path info/exclude`,
  before writing anything. In a linked worktree `.git` is a file, so the literal
  `.git/info/exclude` does not exist. Never touch `.gitignore`: it is tracked.
- **Check every write target** with `git ls-files --error-unmatch <path>`, including
  the file a pointer skill redirects to. A tracked target is left alone, and its
  revision goes in the report as a draft. An exclude entry does not hide a change to a
  tracked file.
- **Write only untracked files**: the skills, and the pointer block in
  `CLAUDE.local.md` beside the `tsh:project-context` block, which stays byte for
  byte. On a re-run these files already exist; being untracked is what matters, and
  repair mode edits them like any other. List each new path in the exclude file
  before writing it, then confirm with `git check-ignore` that each is ignored.
  Delete a new file that is not, and report it as a draft.
- **`CLAUDE.md` is never created or edited** in local mode.
- **A linked worktree** has no `.local` files of its own: they exist only in the main
  checkout, the first entry of `git worktree list`, so this worktree's sessions would
  not see the pointer. Write nothing there. Put both drafts in the report and name the
  main checkout as the place to run this skill.

## 2. The record line

The pointer block (Step 4) ends with one record line, an HTML comment:

```markdown
<!-- tsh:project-checks record: captured at <commit>; declined: <candidate, date>; not project-wide: <invariant, date>; confirmed, drafted only: <candidate or project-wide invariant, date> -->
```

It holds what leaves no other trace:

- **`captured at`**: the current `HEAD`, rewritten on **every** run.
- **Negative answers**: a declined code-only candidate, an invariant the team said is
  not project-wide.
- **Positive answers whose skill was only drafted**: a confirmed candidate or a
  project-wide mark that could not be written into a skill, because the target was
  tracked in local mode, failed `git check-ignore`, or the run was in a worktree.
  Once the skill holding it is written, the entry moves there and leaves the record.

Other positive answers live in the skills themselves. A question with no answer is
recorded nowhere, so the next run asks it again.

## 3. A re-run

Read the block and the generated skills **from disk**: HTML comments are stripped
from the copy in context, so only the files show the record line.

- **Commands.** Check that the recorded commit exists with
  `git cat-file -e <commit>^{commit}`. If it does, a command whose sources show no
  change in `git diff <commit> -- <its sources>` is not re-run. If it does not, as
  after a squash merge of the branch the capture ran on or in a shallow clone, treat
  every command as changed.
- **Invariants.** One whose source is a team confirmation is kept as it stands.
- **Questions.** Nothing already answered, either way, is asked again; an unanswered
  question is.

A second run on an unchanged repository therefore changes nothing and asks only what
is still open.
