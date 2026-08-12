# Change records

Use this flow for CHANGELOG entries, pull request descriptions, release notes, and
migration guides. It covers how the craft rules land on these documents — not what
sections or format a given project requires.

## 1. Who the reader is

Someone answering one question: **does this affect me, and what must I do?** They
are scanning a list of many entries, not reading yours in isolation. An entry that
does not answer that question in its first line will be skipped, and the reader
will find out the hard way later.

## 2. Lead with the effect, not the internals

The reader does not care what you changed. They care what is now different for
them.

> Refactored the session middleware and moved expiry into the token claims.

> Sessions now expire after 24 hours instead of 7 days.

Write the second, and put the first in the body only if a reader needs it to act.

## 3. Name who is affected

"Anyone calling `POST /v1/orders`" is useful. "Users" is not. Being specific lets
most readers stop reading immediately, which is the entire point of the format.

If nobody is affected — an internal refactor with no observable difference — say
that in one line and stop. A change record that pads an invisible change teaches
readers that entries are not worth scanning.

## 4. Breaking changes get the action, not the diagnosis

State what breaks, then the exact change the reader makes. Put the reasoning after
both, or leave it out.

> Due to inconsistencies in how the API handled pagination across endpoints, we
> have undertaken a normalisation effort affecting several response shapes.

> `GET /v1/orders` now returns `{ items, cursor }` instead of a bare array.
> Replace `response.map(…)` with `response.items.map(…)`.

## 5. What bloats these

- The story of the investigation that led to the change.
- A list of every file touched — the diff already says that.
- Restating the ticket instead of linking it.
- "Various improvements and bug fixes."
- Thanks and review credits inside the entry.

## 6. CHANGELOG entries

Append; never rewrite history, even when an old entry is poorly written. Match the
existing entry format exactly — a change record set is read as a series, so
consistency matters more than any one entry's phrasing.

One entry per user-visible change, not per commit. Changes with no observable
effect usually do not belong at all.

## 7. Pull request descriptions

Three things, in this order: what changed, why, and how to verify it. The third is
what reviewers actually need and the one most often missing — name the command to
run, the page to open, or the case to try.

Link the ticket rather than retyping it. Keep the title to the repository's commit
convention; this skill does not govern titles.

## 8. Migration guides

The reader is mid-migration and needs to know where they are. That makes ordering
and resumability the whole job:

- Numbered steps in the order performed, each one independently verifiable.
- State up front what the migration costs: downtime, duration, reversibility.
- Say what to do when a step fails, including how to get back to a working state.
- Put the breaking changes before the optional improvements.

Front-load the answer to "do I need to do this at all?" — a version range, a
feature flag, a config key. Most readers of a migration guide should be able to
leave after the first paragraph.
