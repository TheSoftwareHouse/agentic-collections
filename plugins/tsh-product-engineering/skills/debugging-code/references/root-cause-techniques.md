# Root-cause techniques

Load this when the first hypothesis has failed, or the stack trace does not point at
the faulty line. Each technique below narrows the search space with a check that has a
definite answer. Pick by what you have: a known-good commit → bisect; a failing input →
shrink it; neither → instrument.

## 1. Keep a hypothesis log

Write each hypothesis down before testing it, with the check that would disprove it
and the result:

```text
H1: the cache returns a stale price after an update
    check: log cache hit/miss + value in PriceService.get for the failing SKU
    result: miss on every call — REJECTED
H2: the update writes to the replica, the read goes to the primary
    check: ...
```

This stops two failure modes that waste most debugging time: re-testing a hypothesis
already rejected, and changing two things at once so that neither result means
anything. One hypothesis, one check, one change.

A check that cannot come out against the hypothesis is not a check. "Add a log and see
whether it looks right" fails that test; "log the value and expect `null` if H1 holds"
passes it.

## 2. Bisect when there is a last known good commit

If it worked at some commit and fails now, `git bisect` finds the commit that broke it
in about log₂(n) steps. Automate it with the failing test from step 3 of the skill:

```shell
git bisect start <bad-commit> <good-commit>
git bisect run <command that runs only the repro test>
git bisect reset
```

The command must exit `0` when the commit is good, `1`–`124` or `126`–`127` when bad,
and `125` to skip a commit that cannot be tested (it does not build, say). If the repro
test does not exist at older commits, write it to a file outside the tree and have the
command copy it in before running.

The commit bisect finds is where the bug was *introduced*, not necessarily where the
cause lives. A dependency bump or a config change often surfaces a latent fault
elsewhere; read the diff and keep going until the causal chain is complete.

Bisect also works on dependencies: when an upgrade of several packages broke
something, upgrade them one at a time.

## 3. Shrink the input

When a specific input triggers the bug, cut it in half and keep whichever half still
fails; repeat until nothing more can be removed. Apply the same to configuration
(disable half the feature flags), to a sequence of operations (replay half the event
log), or to code (comment out half of a suspect function in a scratch copy).

The minimal failing case is usually the clearest statement of the root cause, and it
becomes the regression test.

## 4. Instrument temporarily

When nothing points anywhere, observe the actual values along the path:

- Log at the boundaries first — the input entering the failing function and the value
  leaving it — then move inward toward the first place the value is wrong.
- Mark every temporary line so it is trivially found and removed:
  `// DEBUG(<ticket-id>): remove`. Step 6 of the skill requires removing all of it.
- Prefer the debugger or the test runner's inspect mode when the project supports it;
  it needs no cleanup.
- Never add instrumentation that logs secrets, tokens or personal data, even
  temporarily — logs leave the machine.

The first point where an observed value differs from the expected one is where the
cause is, or immediately downstream of it.

## 5. Reading stack traces that mislead

- **Start from your own code.** Skip framework and library frames from the top until
  the first frame in the project's source; the fault is usually there or in the frame
  just below it.
- **Async gaps.** An `await` or a callback breaks the trace, so the frame that
  *scheduled* the failing work may be missing. Look for the caller by searching where
  the failing function is invoked, or enable the runtime's async stack traces.
- **Minified or transpiled code.** A trace pointing into `dist/` or a bundle needs
  source maps. Resolve it against the maps before reading line numbers — the
  untranslated numbers point at the wrong code.
- **Rethrown and wrapped errors.** The trace shown is often the wrapper's. Follow the
  `cause` chain to the original error, and note any place that rethrew without one —
  that loss of context is itself worth a sibling finding.

## 6. Concurrency and shared state

When the failure is intermittent (see `./reproducing-failures.md` §3 for making it
reproducible), look for:

- **Check-then-act** sequences without a lock or a database constraint: read a value,
  decide, write — with another request able to write in between.
- **Lost updates** — two writers read the same version and both save. The fix is
  usually optimistic locking, an atomic update, or a unique constraint, chosen to
  match what the project already uses.
- **Shared mutable state** across requests: module-level variables, singletons
  holding per-request data, a reused client with per-call state.
- **Missing `await`** — a promise that runs after the caller has moved on, or an
  error that never reaches the handler.

## 7. When to stop and ask

Escalate to the user, with the hypothesis log, when:

- three hypotheses in a row have been rejected and the search space is not shrinking,
- the evidence points into a third-party library or service you cannot change,
- confirming a hypothesis would need production access, data or credentials you do
  not have.

A clear account of what has been ruled out is a useful result. Guessing past this
point produces a change nobody can trust.
