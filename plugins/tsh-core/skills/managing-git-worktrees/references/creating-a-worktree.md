# Creating a Worktree

Use this flow only for create requests. Work through the steps in order — the
ordering of fetch, conflict checks, and the two confirmations is what makes the
operation safe.

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
- If the user supplies a path, still derive and show the canonical-root-based
  proposal, then validate the supplied path as the candidate before accepting it;
  normalize it to exactly one absolute path and stop on lookup, normalization, or
  ambiguity failure.
- Reject either the derived or user-supplied candidate if it equals or is nested
  beneath `active_root` or `canonical_root`, already exists, conflicts with an
  existing registered worktree path, or conflicts with an existing registered
  branch name. Reject unsafe, conflicting, or non-unique paths before mutation.
- Do not silently create inside either repository root.

## 4. Fetch the base

- Run `git -C "$canonical_root" fetch origin main`.
- Stop immediately on any fetch failure.
- Verify that `refs/remotes/origin/main` exists.
- Resolve the fetched commit with
  `git -C "$canonical_root" rev-parse refs/remotes/origin/main` and call the result
  `base_commit`.
- Run `git ls-remote --exit-code --heads origin "refs/heads/$branch"`. Exit status
  `2` is the only acceptable absence/no-matching-head result. Exit status `0` means
  the remote branch exists and must cause rejection; any other exit status is
  indeterminate/fatal and must stop the workflow. Never adopt an existing remote
  branch, and stop on any failure.
- Stop if the ref or `base_commit` cannot be resolved.
- Never fall back to local `main`, `HEAD`, or the current feature branch.

## 5. Check conflicts before mutation

- Reject the branch if a registered worktree already uses that branch name.
- Reject the branch if a local branch with that name already exists, even if it is
  not registered to a worktree.
- Reject the branch if remote `refs/heads/<branch>` exists; never adopt an existing
  remote branch.
- Reject the path if a registered worktree already uses that path.
- Reject any path that already exists or is inside the active worktree.
- Do not create anything until all checks pass.

## 6. Present the final literal confirmation

- After fetch and conflict checks, present one final confirmation that contains the
  exact branch name, the shell-safe absolute path, the resolved `base_commit`, and
  the intended upstream `origin/<branch>`.
- Example wording:
  `Create worktree? branch=<branch> path='/abs/path' base=<base_commit> upstream=origin/<branch>`.
- Only this final confirmation authorizes creation; earlier proposals or partial
  confirmations do not.

## 7. Create the local worktree with no tracking

- Create the worktree with
  `git -C "$canonical_root" worktree add --no-track -b "$branch" "$path" "$base_commit"`.
- Treat branch, path, and `base_commit` as untrusted values; pass them as separate
  shell arguments and never concatenate them into a raw command string.

## 8. Verify the created result

- Verify that the created path exists and that
  `git -C "$path" rev-parse --abbrev-ref HEAD` resolves to `$branch`.
- Verify that `git -C "$path" rev-parse HEAD` equals `base_commit`.
- Verify that resolving
  `git -C "$path" rev-parse --abbrev-ref --symbolic-full-name @{upstream}` fails or
  errors because no upstream is configured. If it unexpectedly resolves to any
  upstream, treat that as verification failure, stop, and do not proceed to publish.
- On fetch, creation, or verification failure, stop in a controlled unverified
  state and report the failure; do not report an unverified success.

## 9. Return the terminal command

- Return a copy-paste-ready shell-quoted absolute command such as
  `cd -- '/abs/path'`.

## 10. Confirm the first remote publication separately

- Immediately before the first remote mutation, request a second, separate literal
  confirmation naming exactly the intended upstream `origin/<branch>` and
  `base_commit`.
- Example wording: `Publish upstream? upstream=origin/<branch> base=<base_commit>`.
- This confirmation and the step 6 local-creation confirmation are distinct;
  neither substitutes for the other.

## 11. Publish without force

- After the separate publish confirmation, run exactly
  `git -C "$path" push --set-upstream origin "$branch"`.

## 12. Verify the published upstream

- Verify that `git -C "$path" rev-parse --abbrev-ref --symbolic-full-name @{upstream}`
  resolves exactly to `origin/<branch>`.
- Verify that `git -C "$path" rev-parse HEAD` equals `base_commit`.
- Verify that `git -C "$path" rev-parse "refs/remotes/origin/$branch"` equals
  `base_commit`.
- On any publish or verification failure, report that no verified upstream exists
  yet; preserve the local worktree and branch unchanged. Never automatically
  force-push, retarget, delete, or adopt a race-created remote branch.
- Report full success only after all publication verification passes.
