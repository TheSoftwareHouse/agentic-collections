# Work items

Use this flow for tickets, user stories, acceptance criteria, and bug reports. It
covers how the craft rules land on these documents. It does **not** define what a
user story must contain or how TSH structures acceptance criteria — that belongs to
the skill that owns the artifact, and this one governs only the prose inside it.

## 1. Who the reader is

Three readers in sequence, and the item has to serve all of them:

- Someone in refinement, deciding whether to pick this up and how big it is.
- Someone implementing it, deciding what to build.
- Someone verifying it, deciding whether it is finished.

The third reader is the one authors forget, and the reason acceptance criteria have
to be checkable by a person who did not write them.

## 2. Front-load the outcome, not the origin

> During last week's retro we noticed that several customers had contacted support
> about login problems, and after looking into it we found…

> Users cannot reset a password without contacting support.

The first sentence states the problem or the desired outcome. Everything about how
the item came to exist goes later, or nowhere.

## 3. Cut the origin narrative

Where a requirement came from is almost never actionable. One link to the source —
the conversation, the ticket, the research — beats three paragraphs summarising it.
Nobody will read a summary of a discussion they were not part of and can no longer
influence.

## 4. Make "done" unambiguous

Every acceptance criterion must be answerable yes or no by someone who did not
write it. That is the whole test.

| Not a criterion | A criterion |
| --- | --- |
| Password reset works correctly | A reset link sent to a registered address logs the user in and expires after 30 minutes |
| The page is performant | The page renders its first result within 1 second on a throttled 3G profile |
| Errors are handled | An expired reset link shows the "link expired" page with a resend action |

If you cannot write the checkable version, the requirement is not yet understood —
say so in the item rather than covering it with a vague criterion.

## 5. Bug reports lead with observed versus expected

The first two lines: what happened, and what should have happened. Then
reproduction steps, then environment. The narrative of how you found it goes last,
or not at all.

> Deleting the last item in a cart returns a 500. Expected: an empty cart and a 200.

Do not speculate about the cause in the report. A wrong guess in the first
paragraph anchors whoever picks it up and costs more time than it saves. If you
have evidence, give the evidence — the log line, the failing request — not the
theory.

## 6. What bloats these

- Pasted chat threads instead of the conclusion drawn from them.
- Solution design inside a story, when the story should state the outcome.
- Repeating the epic's context in every child item.
- "As a user, I want…" phrasing that adds no information the plain sentence lacks.
- Screenshots of text.
- Restating the acceptance criteria in the description, in different words.

## 7. Say what is out of scope

One line, when there is a plausible reading that would enlarge the work. It costs a
sentence and prevents the most common form of scope drift, which is an implementer
reasonably inferring more than was asked.

## 8. Link, do not retype

Designs, specs, related items, and prior art get links. A retyped copy goes stale
silently, and the reader cannot tell which version they are looking at.
