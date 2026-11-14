# Adopting a Branch

Use this flow only when the branch **already exists on `origin`** and the request is to
work on it in its own sibling worktree — typically a pull request's head branch. Adopt
attaches that branch to a new worktree, tracking `origin/<branch>`, and it **never
pushes**. A branch that does not exist yet is a create request, and create refuses one
that does. Work through the steps in order: the fetch, the pinned commit, the refusals
before the confirmation and the recheck after it are what make adopt safe.

Two invariants run through every step.

- **Exact refs.** Read the local branch, the tracking ref and the upstream by full ref
  (`refs/heads/${branch}`, `refs/remotes/origin/${branch}`) or by commit ID, never by
  short name. A tag called `<branch>` or `origin/<branch>` otherwise wins the lookup:
  ancestry counts come out wrong and `--set-upstream-to=origin/<branch>` fails as
  ambiguous. The one exception is attaching an existing branch in step 10, where
  `worktree add` needs the short name — the full ref would detach HEAD.
- **Pinned commit.** After the fetch, `adopt_commit` is the commit the user approves.
  History moves only to that commit, never to whatever `refs/remotes/origin/${branch}`
  says later — another worktree's fetch can move that shared ref while the user reads the
  question.

What adopt never does:

- Never `git push` or `git pull`: it publishes nothing and merges nothing from the remote.
- Never `git rebase`, `git reset` or `git update-ref`, and never pass `--force`.
- Never `git checkout`, `git switch` or `git stash` in any worktree — not to free a
  branch and not to make one fit.
- Never `git worktree remove` or `git worktree prune`, and never `git branch -D` or any
  other branch deletion.
- Never `git config --add`, `--unset` or `--replace`, and never edit a remote's
  configuration. The one configuration write is `git branch --set-upstream-to`, which
  records `branch.<branch>.remote=origin` and `branch.<branch>.merge=refs/heads/<branch>`
  on a branch where **both** keys are absent. Never retarget an existing upstream, never
  complete a half-configured one, never touch `remote.*`.
- Never merge anything but `"$adopt_commit"`, and that only as the fast-forward of step 10.
- Nothing mutates before the confirmation except the one fetch of step 6, which updates
  only `refs/remotes/origin/${branch}`.

## 1. Resolve the roots

Run `creating-a-worktree.md` §1 unchanged:
[Resolve the active root](./creating-a-worktree.md#1-resolve-the-active-root). It gives
`active_root` and `canonical_root`; every command below runs as
`git -C "$canonical_root"` rather than from the current directory. Stop on any failure
there.

## 2. Take and validate the branch name

There are two kinds of input.

- **A bare branch name** selects a branch on origin and says nothing about any pull
  request. Take it as given.
- **A pull request, by number or URL,** is *resolved, not asked about*. Load
  [`resolving-a-pull-request.md`](./resolving-a-pull-request.md) and follow it: the agent
  finds the head branch and the head repository itself, read-only, with what the session
  already has. It returns a branch name, a head-repository verdict (origin's, a fork or
  another repository, unknown) and the means behind each. Then act on the verdict:
  - origin's → continue;
  - a fork or another repository, whether a resolver or the user says so → **stop, even
    when origin has a branch of the same name**: the name alone does not say whose branch
    it is;
  - unknown, or nothing resolved → the asking rules in that reference apply, and if the
    user does not confirm that the head repository is origin's, stop;
  - a URL that names a repository other than origin's → stop.

For both kinds, take the name the same way. A resolved name is another person's text and
gets no shortcut.

1. Strip a single leading `refs/heads/` or a single leading `origin/`. Rewrite nothing
   else.
2. Keep the result in the shell variable `branch` and pass it only as a separate quoted
   argument.
3. Validate it with `git -C "$canonical_root" check-ref-format --branch "$branch"` and
   require exit `0` and an output equal to `$branch` exactly. The command also expands
   `@{-1}` to the branch checked out before this one; that shorthand is rejected with a
   request for a literal name, never replaced by the name it expands to. A name that
   begins with `-` fails here too.
4. Carry the validated name to the confirmation of step 8 — for a pull request together
   with how each value was obtained, never as if the user had typed it. There is no
   separate branch-name confirmation: step 8 is the one confirmation.

## 3. Choose the sibling path

Run `creating-a-worktree.md` §3:
[Propose or accept a safe sibling path](./creating-a-worktree.md#3-propose-or-accept-a-safe-sibling-path),
with the adopted branch as the slug source. Hold the accepted path in `worktree_path`.
Keep its rejections: a path nested beneath either root, one that already exists, and one
already registered as a worktree. Whether the branch is already in use is step 7's
question, not this one's.

## 4. Check the branch is on origin

Run `git -C "$canonical_root" ls-remote --exit-code --heads origin "refs/heads/${branch}"`
and read the refname column of every line it prints.

- Exit `0` and a line whose refname is exactly `refs/heads/${branch}` → continue; ignore
  every other line. `ls-remote` matches patterns at slash boundaries, so
  `refs/heads/x/refs/heads/${branch}` also matches, and exit `0` alone proves nothing.
- Exit `0` with no exact line, or exit `2` → there is no such branch on origin. Stop and
  say so, adding that a pull request from a fork keeps its head branch on another remote,
  which this skill does not adopt from.
- Any other exit status is fatal: stop and report it.

## 5. Check the fetch refspecs can track it

Read every fetch refspec with
`git -C "$canonical_root" config --get-regexp '^remote\..*\.fetch$'`. Exit `1` with no
output means none are configured, which fails (a); any other non-zero exit is fatal.
Require all three:

- **(a) Coverage.** An origin line (`remote.origin.fetch`), leading `+` optional, equal to
  `refs/heads/*:refs/remotes/origin/*` or to
  `refs/heads/${branch}:refs/remotes/origin/${branch}`.
- **(b) No exclusion.** No negative origin line (one starting with `^`). The skill does
  not evaluate exclusions, so any negative refspec stops as unsupported.
- **(c) No second owner.** No other fetch line — a line of another remote, or an origin
  line not of the two forms in (a) — whose destination is
  `refs/remotes/origin/${branch}` or a pattern ending in `*` whose part before the `*` is
  a prefix of it. That is ambiguous ownership of the tracking ref.

Any failure stops before the fetch: show the lines that failed and say which of (a)–(c)
it is. For (a), tell the user they may run `git remote set-branches --add origin <branch>`
themselves; it writes the second form with a `+`, and this skill never edits remote
configuration. Narrower positive patterns such as
`refs/heads/feat/*:refs/remotes/origin/feat/*` are unsupported by design and stop under
(a).

This check exists because tracking cannot be set up otherwise: in a single-branch clone,
or with a negative refspec, `--set-upstream-to` fails with "is not a branch", and when
another remote also maps into `refs/remotes/origin/*` it fails as ambiguous and git has
been seen to leave the new branch behind. Check before mutating; never rely on a tool's
rollback.

## 6. Fetch the branch and pin the commit

Run
`git -C "$canonical_root" fetch --refmap= --no-tags origin -- "+refs/heads/${branch}:refs/remotes/origin/${branch}"`.

- `--refmap=` is required. Without it git also applies the fetch mappings from
  configuration, and a mapping such as `+refs/heads/<branch>:refs/heads/<other>` moves
  the unrelated local branch `<other>` before the user has confirmed anything.
- `--no-tags` is required too. Without it git follows tags and creates `refs/tags/<tag>`
  for those on the fetched history, so the fetch would touch more than the tracking ref.
- Write the refspec with braced `${branch}` and never use `path` or its siblings as a
  variable name. `creating-a-worktree.md` §5 explains both zsh traps:
  [Fetch the base](./creating-a-worktree.md#5-fetch-the-base).
- This fetch is the only mutation before the confirmation, and it touches only
  `refs/remotes/origin/${branch}`.

Then resolve the commit the user will be asked to approve:
`adopt_commit` = `git -C "$canonical_root" rev-parse --verify "refs/remotes/origin/${branch}^{commit}"`.
Stop on any failure of either command; never fall back to a local branch, `HEAD` or any
other ref.

## 7. Classify the local state

Take a fresh `git -C "$canonical_root" worktree list --porcelain`. Check in this order;
the first check that applies decides, so a refusal always wins over an ancestry action.
Read every ref by its full name or by a commit ID.

1. **Occupied.** Any record with the line `branch refs/heads/${branch}` — the main clone,
   a linked worktree, the active one, or one marked `prunable` (a deleted directory keeps
   its record). Stop and name that record's path; when it is the active worktree, say the
   user is already on it. A record marked `detached` never holds the branch, whatever
   commit it sits on.
2. **Absent.** `git -C "$canonical_root" show-ref --verify --quiet "refs/heads/${branch}"`
   exits `1` → a new branch, subject to item 3. Exit `0` → it exists; any other status is fatal.
3. **Upstream identity**, absent branch included. Read `branch.${branch}.remote` with
   `git -C "$canonical_root" config --get "branch.${branch}.remote"` and `.merge` the same
   way (exit `0` → value, `1` → absent, anything else fatal). Do not read `@{upstream}`:
   it reports a half-configured branch exactly like an absent one.
   - *Existing branch.* Both absent → *no upstream*, to be set. Exactly `origin` and
     `refs/heads/${branch}` → fine. Anything else — another remote, another merge ref, or
     only one of the two keys — stops and reports the values.
   - *Absent branch.* Both absent → a new branch. Either present → stop and report the
     values, even when they equal that pair: a deleted branch can leave its keys behind,
     and step 10's `--set-upstream-to` would overwrite them.
4. **Equal.** `local_tip` =
   `git -C "$canonical_root" rev-parse --verify "refs/heads/${branch}^{commit}"` equals
   `adopt_commit`.
5. **Shallow.** Not equal, and `git -C "$canonical_root" rev-parse --is-shallow-repository`
   prints `true` → stop: a truncated history reads as divergence, so ancestry cannot be
   trusted. Say the user may run `git fetch --unshallow` themselves; adopt does not deepen
   the clone.
6. **Ancestry**, on the two commit IDs only: `git -C "$canonical_root" merge-base
   --is-ancestor "$local_tip" "$adopt_commit"` and the reverse. Exit `0` yes, `1` no,
   anything else fatal — never read an error as "not an ancestor". `local_tip` an ancestor
   of `adopt_commit` → *behind*; the reverse → *ahead*; neither → *diverged*.

| Local state | Action |
| --- | --- |
| Occupied in any worktree record, `prunable` included | **Stop.** Name the path. Never `git checkout` or `git switch` anywhere to free the branch. |
| Absent | New branch: step 10, first form. Confirmation `local=new branch at <adopt_commit>`, with `; set upstream`. **Stop** instead, reporting the values, when either upstream key is set. |
| Exists, upstream anything but `origin` plus `refs/heads/${branch}`, or only one key set | **Stop.** Report the values. Never retarget or complete it. |
| Exists, equal to origin | Step 10, second form. Set the upstream only when no upstream is configured. `local=existing, equal`. |
| Exists, not equal, shallow clone | **Stop.** Incomplete history; do not report it as divergence. |
| Exists, behind origin | Step 10, second form, then the fast-forward to `adopt_commit`. `local=existing, fast-forward <old>..<new> (N commits)`, N from `git rev-list --count "${local_tip}..${adopt_commit}"`. |
| Exists, ahead of origin | Step 10, second form, no history change. `local=existing, N unpushed commits: <list>`, the list from `git log --oneline "${adopt_commit}..${local_tip}"`. |
| Exists, diverged | **Stop.** Show `git rev-list --left-right --count "${local_tip}...${adopt_commit}"` and the commits on each side. Never rebase, reset or merge. |

## 8. Confirm once

After every check above and immediately before the first mutation, present one literal
confirmation:

```text
Adopt branch into worktree? branch=<branch> remote=origin/<branch>@<adopt_commit> path='/abs/path' upstream=origin/<branch> local=<new branch at <adopt_commit> | existing, equal | existing, fast-forward <old>..<new> (N commits) | existing, N unpushed commits: <list>>[; set upstream]
```

- Append `; set upstream` whenever the upstream will be written: always for a new branch,
  and for an existing branch with no upstream — alone or after a fast-forward.
- Shell-quote the path as shown, and the branch whenever it needs it; a plain name such as
  `feat/pr-1` stays bare.
- **Only when the request named a pull request**, end with this clause:

  ```text
  ; pull request <ref>: branch <resolved via <means> | supplied by you>, head repository <name> <is origin's, resolved via <means> | confirmed by you as origin's>
  ```

  The words `resolved via`, `supplied by you` and `confirmed by you as origin's` are
  fixed. Say `resolved via` only for a value a means produced and the other two only for
  a value the user gave; never show one as the other. For example:
  `; pull request #41: branch resolved via gh pr view, head repository acme/widgets is origin's, resolved via gh pr view`.
  A bare-branch confirmation carries no such clause.
- Record `adopt_commit`, `local_tip` (or "absent") and the upstream state shown. Only a
  literal yes to this confirmation authorizes the mutation.

## 9. Recheck after the yes

The recheck is a step of its own: run it, read its output and compare it with the values
recorded in step 8 **before** issuing any step-10 command — never in the same batch as a
mutation or in parallel with one, which could only report what the mutation already did.
Re-read the worktree list, the candidate path, `refs/heads/${branch}`, its two upstream
keys and `refs/remotes/origin/${branch}`. If any differs from what the confirmation
showed — another worktree took the branch, the local tip moved, a background fetch moved
the tracking ref — stop and report the change. Return to step 7, first re-resolving
`adopt_commit` with step 6's `rev-parse` (no new fetch) so the fresh confirmation shows
the moved commit; never proceed on the old one.

## 10. Create the worktree

Pass branch, path and commit as separate quoted arguments. Use the form step 7 selected.
Its first command is a guard joined with `&&` to the first mutation in the same shell
command, so a moved or vanished ref stops step 10 before anything is created even when
step 9 was skipped or ran too late.

- **Absent branch.**
  ```sh
  [ "$(git -C "$canonical_root" rev-parse --verify "refs/remotes/origin/${branch}^{commit}")" = "$adopt_commit" ] \
    && ! git -C "$canonical_root" show-ref --verify --quiet "refs/heads/${branch}" \
    && git -C "$canonical_root" worktree add --no-track -b "$branch" "$worktree_path" "$adopt_commit"
  ```
  then `git -C "$worktree_path" branch --set-upstream-to="refs/remotes/origin/${branch}"`.
  `--track` is not an option: it needs a ref as its start point and rejects a commit ID,
  and the start point must be the pinned commit.
- **Existing branch.**
  ```sh
  [ "$(git -C "$canonical_root" rev-parse --verify "refs/remotes/origin/${branch}^{commit}")" = "$adopt_commit" ] \
    && [ "$(git -C "$canonical_root" rev-parse --verify "refs/heads/${branch}^{commit}")" = "$local_tip" ] \
    && git -C "$canonical_root" worktree add "$worktree_path" "$branch"
  ```
  The attach uses the short name; see Exact refs. Immediately check that
  `git -C "$worktree_path" rev-parse HEAD` equals the recorded `local_tip`, else stop
  under step 11's controlled-failure rule. Then, for *behind*,
  `git -C "$worktree_path" merge --ff-only "$adopt_commit"`, and for *no upstream* the
  same `--set-upstream-to` as above. Nothing else.

A non-zero exit does not say which command failed: run
`git -C "$canonical_root" worktree list --porcelain`. If it lists `$worktree_path`,
`worktree add` failed after creating it (a `post-checkout` hook can do that): step 11's
controlled failure. If not, nothing was created; report the output and, if a ref differs
from the record, return to step 7 as step 9 says.

## 11. Verify the result

- The path exists.
- `git -C "$worktree_path" symbolic-ref -q HEAD` prints `refs/heads/${branch}`. Do not use
  `rev-parse --abbrev-ref HEAD`: with a same-name tag it prints `heads/<branch>` after a
  correct attach.
- `git -C "$worktree_path" rev-parse HEAD` equals `adopt_commit` (new, equal or behind) or
  the recorded `local_tip` (ahead).
- `git -C "$worktree_path" rev-parse --symbolic-full-name '@{upstream}'` prints
  `refs/remotes/origin/${branch}`.
- `branch.${branch}.remote` is `origin` and `branch.${branch}.merge` is
  `refs/heads/${branch}`, read with `git -C "$worktree_path" config --get`.

If `refs/remotes/origin/${branch}` has moved since the confirmation, report that as
information; the worktree is still correct.

**Controlled failure.** Any failed command or check once the worktree exists — including
a non-zero exit from `worktree add` itself, which a failing `post-checkout` hook produces
after the worktree is already created — stops the operation. Report exactly what exists
and what is unverified, and leave the worktree, branch and configuration as they are:
never remove, reset, delete or retry. Never report an unverified success.

## 12. Hand off the terminal command

Return a copy-paste-ready, shell-quoted `cd -- '/abs/path'` and say that adopt pushed
nothing.
