# Detecting candidates

Read this before naming a single candidate. Detection is the step where a retro either
earns trust or loses it, and the failure is asymmetric: a missed candidate costs one
improvement, while a padded list costs the reader's willingness to read the next retro
at all.

## What a candidate is

A candidate is a **specific, recurring friction with a named trigger** — not a topic the
session touched, and not something that went badly once.

Three things have to be true at the same time:

1. It happened **more than once**, and you can quote both occurrences.
2. It will happen **again**, at a moment you can name.
3. Something in the toolchain could have **absorbed** it — a skill, a subagent, a hook,
   a plugin, or a line in a memory file.

Fail any one of the three and it is not a candidate. Record it as a rejection.

## The signal catalogue

Each row is a pattern to look for in the session, with the primitive it usually implies.
**The primitive column is a hypothesis, not a verdict** — Step 3 of the procedure
confirms it against
[`authoring-claude-extensions`](../../authoring-claude-extensions/SKILL.md), which owns
the routing decision.

| Signal in the session | Usually implies |
| --- | --- |
| The same multi-step procedure was reconstructed, pasted or re-explained | A skill |
| The user typed a near-identical prompt to start a task more than once | A skill, user-invocable |
| Claude got a project convention wrong and was corrected twice or more | A memory file — `CLAUDE.md` or a path-scoped rule |
| Claude searched broadly, dumped output nobody re-read, then used one line of it | A subagent |
| Several independent readings or opinions were needed on one question | A subagent |
| Something had to hold every time and Claude decided not to do it | A hook, not stronger wording |
| A verification step was skipped and had to be demanded | A hook |
| The same setup was described as needed in another repository or by another team | A plugin |
| Guidance was needed while *creating* a file that did not exist yet | A skill — a path-scoped rule fires on read and can never arrive in time |

The last row is the one that gets mis-assigned most often, and it is worth checking
explicitly: ask whether the guidance was needed *before* the file existed. If so, no
rule scoped to that path could ever have helped.

## The evidence bar

For each candidate, write these down before it goes in the file. If you cannot fill a
line, the candidate is rejected.

- **Occurrences** — at least two, quoted, each with where in the session it happened.
  Paraphrase is not evidence; the quote is what lets a reader check you.
- **Trigger** — the concrete moment it will fire again. "When someone works on
  authentication" is not a trigger. "When a new plugin directory is created and needs a
  marketplace entry" is.
- **Absorbable** — name what the extension would have done instead. If the answer is
  "reminded Claude to be more careful", there is no extension here.
- **Rejected alternative** — the primitive you considered and turned down, with the
  reason. This is what a reviewer needs in order to disagree, and having to name one
  catches assignments made on autopilot.

Two occurrences is a floor, not a target. A candidate with two weak occurrences and no
nameable trigger is weaker than one with two strong ones — mark the first `tentative`
and say why.

## False positives

These look like candidates and are not. Each has been the source of a padded retro.

**A one-off.** The session did something unusual once and it went fine. Novelty is not
friction.

**A genuinely novel task.** Hard work is not repeated work. A difficult debugging
session with no repetition in it yields no candidates, and that is the correct result.

**Something already covered.** The convention is already in `CLAUDE.md`, the skill
already exists, the hook is already configured — and the real finding is that it did not
fire. That is a *fix to an existing extension*, which is a legitimate candidate, but it
must be written as one: name the existing artifact and what failed about it, not a new
extension beside it. Two extensions with overlapping descriptions make routing a coin
flip, and the loser is silently never invoked.

**A preference, not a procedure.** "The user likes short commit messages" is a memory
file line at most, and often just a preference already recorded. Do not propose a skill
for it.

**Friction caused by this session's own mistakes.** If Claude misread a file and then
had to backtrack, the fix is not an extension. Distinguish *the tool did not exist* from
*the tool existed and was not used*.

**Anything whose evidence is the plan rather than the session.** A plan listing five
future steps is not five occurrences. Evidence comes from what happened.

## Scoping with `$ARGUMENTS`

When the user named a focus, restrict detection to that thread — but still report the
scope in the file's header, so a later reader knows the retro was partial by
instruction rather than by oversight. Do not silently widen the scope because a
promising candidate sits just outside it; note it in one line under rejected candidates
with `out of requested scope` as the reason.

## When nothing clears the bar

Say so, in the file and in the report. A retro over a short, clean session should
usually find nothing, and a skill that always finds something is a skill nobody will
trust twice. Write the header, write the rejected candidates with their reasons, and
stop.
