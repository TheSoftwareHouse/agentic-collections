# Removing a Worktree

Use this flow only for remove requests. Removal is destructive; the refused-target
list below is exhaustive and force behavior is unsupported.

## 1. Analyze a fresh porcelain list before anything else

- Run `git worktree list --porcelain` from the repository root.
- Resolve exactly one target by either an exact normalized absolute path or an
  exact branch name.
- Stop on no match, multiple matches, or any ambiguity; never guess.

## 2. Refuse the unsafe default targets

- Refuse the active worktree, the main worktree, a locked target, and a prunable
  target.
- Inspect cleanliness before removal, including tracked modifications and untracked
  files.
- Stop on dirty or untracked state and explain that force removal is unsupported in
  this skill.
- Never use `git worktree remove --force`.

## 3. Show the exact target and ask for literal confirmation

- Display the exact target path plus its branch or detached state.
- Ask for a literal confirmation immediately before removal.
- Only after explicit confirmation may the workflow proceed to safe non-force
  removal.

## 4. Remove safely after confirmation

- Prefer `git worktree remove -- <absolute-target-path>` with the untrusted path
  passed as a separate argument.
- Treat the path as untrusted and quote it in any user-facing display.
- If the removal command fails, stop and report the failure; do not report an
  unverified success.

## 5. Verify the removal result

- Run a fresh `git worktree list --porcelain` after removal.
- Confirm that the target worktree record is gone before reporting success.
- If the target still appears, stop and report the unresolved state.

## 6. Ask separately about local branch deletion

- After successful worktree removal, ask a second question about deleting the
  associated local branch.
- This is a separate decision from worktree removal and is never implicit
  authorization.
- If the target is detached, treat it as having no associated local branch.
- If the user approves branch cleanup and the target has an associated local
  branch, use `git branch -d -- <branch>`.
- If Git refuses because the branch is unmerged, preserve the branch and report the
  refusal; never use `git branch -D` as an automatic fallback.
