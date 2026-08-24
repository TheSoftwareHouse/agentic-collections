# Creating a Worktree

Use this flow only for create requests. Work through the steps in order — the
ordering of base resolution, fetch, conflict checks, and the two confirmations is
what makes the operation safe.

## 1. Resolve the active root

- Run `git rev-parse --show-toplevel` from the current repository.
- Normalize the result to one absolute directory and call it `active_root`; stop
  immediately if it cannot be resolved or normalized exactly once.
- Run `git -C "$active_root" rev-parse --path-format=absolute --git-common-dir` as
  the authoritative metadata lookup for the shared Git directory. Require exactly
  one non-empty absolute result, normalize it without ambiguity, and stop if the
  lookup, normalization, or metadata availability fails.
- Derive `canonical_root` as the parent of that normalized common Git directory.
  Validate that it is exactly one existing, usable worktree root: it must resolve
  back to itself through Git and appear as exactly one normalized worktree path in
  a fresh `git worktree list --porcelain` snapshot. Stop rather than guessing if
  the candidate is missing, ambiguous, unrelated, or otherwise unavailable. Do not
  use the active linked-worktree path, current branch, or an unrelated directory
  as a fallback.
- When `active_root` is the linked worktree, treat it and `canonical_root` as
  distinct roots. When it is the canonical worktree, both values may be the same
  validated root.

## 2. Confirm the branch name

- If the user supplied a branch name, present it as a proposal and ask for
  confirmation anyway.
- Accept it, edit or replace it, or ask for feedback-based regeneration until the
  user explicitly accepts a specific branch name.
- Keep the branch value in a shell variable and shell-quote any user-facing output.

## 3. Propose or accept a safe sibling path

- Derive the default sibling absolute path as
  `<canonical-parent>/<canonical-root-basename>-<branch-slug>`, where the parent
  and basename come from the validated `canonical_root` (for example,
  `$(dirname "$canonical_root")/$(basename "$canonical_root")-<branch-slug>`).
- Example: canonical root `/Users/you/dev/acme-api`, active linked worktree
  `/Users/you/dev/acme-api-fix-flaky-login-test`, and branch slug
  `feat-checkout-flow` produce `/Users/you/dev/acme-api-feat-checkout-flow`. Note
  that the sibling is derived from the **canonical** root's basename, never from
  the active linked worktree's.
- The slug always comes from the **new branch**, never from the base branch. The
  two are independent values, and a path named after the base tells the user
  nothing about what the worktree is for.
- If the user supplies a path, still derive and show the canonical-root-based
  proposal, then validate the supplied path as the candidate before accepting it;
  normalize it to exactly one absolute path and stop on lookup, normalization, or
  ambiguity failure.
- Hold the accepted absolute path in a shell variable named `worktree_path` — never
  `path`, which destroys `PATH` in zsh. See step 5.
- Reject either the derived or user-supplied candidate if it equals or is nested
  beneath `active_root` or `canonical_root`, already exists, conflicts with an
  existing registered worktree path, or conflicts with an existing registered
  branch name. Reject unsafe, conflicting, or non-unique paths before mutation.
- Do not silently create inside either repository root.

## 4. Resolve the base branch

- Determine `base_branch` by precedence and stop at the first that succeeds:
  1. The base branch the user named, if they named one.
  2. Origin's own default branch, read from the remote with
     `git -C "$canonical_root" ls-remote --symref origin HEAD` and taken from the
     `ref: refs/heads/<name>` line of the output.
  3. Neither resolved — stop and ask the user which branch to base on.
- Record whether `base_branch` was **user-supplied** or **detected**; step 7 has to
  disclose which.
- Normalize the candidate by stripping a single leading `refs/heads/` or a single
  leading `origin/`. The result is the bare branch name. Rewrite nothing else.
- Validate the candidate with
  `git -C "$canonical_root" ls-remote --exit-code --heads origin "refs/heads/$base_branch"`.
  Exit status `0` is the only acceptable result. Exit status `2` means no such
  branch on `origin` and must cause rejection that says so specifically; any other
  exit status is indeterminate/fatal and must stop the workflow.
- Any branch that exists on `origin` is a legal base, feature branches included.
- That same check is what refuses tags, commit SHAs, local-only branches, and
  branches on other remotes such as `upstream/main` — none of them match
  `refs/heads/*` on `origin`. Do not add a separate resolution path for any of
  them; report the rejection and stop.
- Reject the request if `base_branch` equals the new `branch`.
- Never infer the base from local state. `refs/remotes/origin/HEAD` can be stale or
  absent, and `init.defaultBranch` describes this machine rather than this remote.
- Never substitute a different base when the requested one is missing, and never
  assume `main` when detection fails. Stop instead.

## 5. Fetch the base

- Run
  `git -C "$canonical_root" fetch origin -- "+refs/heads/${base_branch}:refs/remotes/origin/${base_branch}"`.
- The explicit refspec is required, not stylistic. A refspec-less
  `git fetch origin <branch>` only guarantees `FETCH_HEAD`, so under a non-default
  fetch refspec or a single-branch clone the remote-tracking ref below can still
  hold a stale commit while this step appears to have succeeded.
- Write the refspec with **braced** `${base_branch}`, never bare `$base_branch`. In
  zsh — the macOS default — `"$base_branch:refs/…"` is parsed as the `:r` history
  modifier, which swallows the `:r` and yields a corrupt one-sided refspec such as
  `+refs/heads/my-brancefs/remotes/origin/my-branch`. It fails loudly rather than
  fetching the wrong thing, but only the braced form works in both shells.
- The same shell dictates scratch variable **names**. In zsh, `path`, `cdpath`,
  `fpath` and `manpath` are arrays tied to `PATH`, `CDPATH`, `FPATH` and `MANPATH`,
  so `path='/some/dir'` silently replaces `PATH` with that single entry and every
  later command in the shell dies with `command not found: git`. Never use those
  names, or their uppercase counterparts, to hold a working value — this flow uses
  `worktree_path`. The symptom reads as a broken environment or a denied sandbox
  rather than a naming bug, so it costs a diagnostic detour every time.
- Stop immediately on any fetch failure.
- Verify that `refs/remotes/origin/$base_branch` exists and call it `base_ref`.
- Resolve the fetched commit with `git -C "$canonical_root" rev-parse "$base_ref"`
  and call the result `base_commit`.
- Stop if `base_ref` or `base_commit` cannot be resolved.
- Never fall back to a local branch of the same name, `HEAD`, or the current
  feature branch.

## 6. Check conflicts before mutation

- Reject the branch if a registered worktree already uses that branch name.
- Reject the branch if a local branch with that name already exists, even if it is
  not registered to a worktree.
- Reject the branch if it already exists on the remote. Run
  `git ls-remote --exit-code --heads origin "refs/heads/$branch"`. Exit status `2`
  is the only acceptable absence/no-matching-head result. Exit status `0` means the
  remote branch exists and must cause rejection; any other exit status is
  indeterminate/fatal and must stop the workflow. Never adopt an existing remote
  branch, and stop on any failure.
- Reject the path if a registered worktree already uses that path.
- Reject any path that already exists or is inside the active worktree.
- Do not create anything until all checks pass.

## 7. Present the final literal confirmation

- After base resolution, fetch, and conflict checks, present one final confirmation
  that contains the exact branch name, the base as `origin/<base_branch>` together
  with the resolved `base_commit`, the shell-safe absolute path, and the intended
  upstream `origin/<branch>`.
- Example wording:
  `Create worktree? branch=<branch> base=origin/<base_branch>@<base_commit> path='/abs/path' upstream=origin/<branch>`.
- Name the base branch; never present the base as a bare commit. A SHA on its own
  gives the user no way to notice that the wrong trunk was used.
- When `base_branch` was detected rather than user-supplied, say so inline, for
  example `base=origin/develop (origin's default) @<base_commit>`.
- Only this final confirmation authorizes creation; earlier proposals or partial
  confirmations do not.

## 8. Create the local worktree with no tracking

- Create the worktree with
  `git -C "$canonical_root" worktree add --no-track -b "$branch" "$worktree_path" "$base_commit"`.
- Treat branch, base branch, path, and `base_commit` as untrusted values; pass them
  as separate shell arguments and never concatenate them into a raw command string.

## 9. Verify the created result

- Verify that the created path exists and that
  `git -C "$worktree_path" rev-parse --abbrev-ref HEAD` resolves to `$branch`.
- Verify that `git -C "$worktree_path" rev-parse HEAD` equals `base_commit`.
- Verify that resolving
  `git -C "$worktree_path" rev-parse --abbrev-ref --symbolic-full-name @{upstream}`
  fails or errors because no upstream is configured. If it unexpectedly resolves to
  any upstream, treat that as verification failure, stop, and do not proceed to
  publish.
- On resolution, fetch, creation, or verification failure, stop in a controlled
  unverified state and report the failure; do not report an unverified success.

## 10. Return the terminal command

- Return a copy-paste-ready shell-quoted absolute command such as
  `cd -- '/abs/path'`.

## 11. Confirm the first remote publication separately

- Immediately before the first remote mutation, request a second, separate literal
  confirmation naming exactly the intended upstream `origin/<branch>`, the base
  `origin/<base_branch>`, and `base_commit`.
- Example wording:
  `Publish upstream? upstream=origin/<branch> base=origin/<base_branch>@<base_commit>`.
- This confirmation and the step 7 local-creation confirmation are distinct;
  neither substitutes for the other.

## 12. Publish without force

- After the separate publish confirmation, run exactly
  `git -C "$worktree_path" push --set-upstream origin "$branch"`.

## 13. Verify the published upstream

- Verify that `git -C "$worktree_path" rev-parse --abbrev-ref --symbolic-full-name @{upstream}`
  resolves exactly to `origin/<branch>`.
- Verify that `git -C "$worktree_path" rev-parse HEAD` equals `base_commit`.
- Verify that `git -C "$worktree_path" rev-parse "refs/remotes/origin/$branch"` equals
  `base_commit`.
- On any publish or verification failure, report that no verified upstream exists
  yet; preserve the local worktree and branch unchanged. Never automatically
  force-push, retarget, delete, or adopt a race-created remote branch.
- Report full success only after all publication verification passes.
