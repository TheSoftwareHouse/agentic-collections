# Decision records

Use this flow for architecture decision records, RFCs, and technical proposals. It
covers how the craft rules land on these documents — not which sections a given
ADR format requires.

## 1. Who the reader is

Two readers, and they want the same thing:

- The reviewer deciding now, who needs the decision and its cost.
- The engineer eighteen months from now asking "why is it like this?", who needs
  the decision and the constraint that produced it.

Neither wants the deliberation. The deliberation is how you arrived at the
document; it is not the document.

## 2. Decision first, always

The first sentence states the decision in the present tense, as settled fact. Then
the consequences. Then the reasoning. Then, briefly, the alternatives.

> This document explores options for our background job infrastructure. We have
> several requirements to consider…

> We run background jobs on Postgres-backed queues rather than Redis or SQS.

A reader who stops after the first sentence should still leave with the answer.

## 3. Compress the alternatives

Each rejected option gets one line: what it was, and the single reason it lost.

Multi-paragraph fair hearings for options you rejected are the largest source of
bloat in decision records, and they are written for the author's comfort rather
than the reader's use. Give the option a line; if a reader wants to reopen it,
the line tells them which constraint to attack.

| Option | Why not |
| --- | --- |
| Redis queues | Adds a component with no durability guarantee we can rely on |
| SQS | Ties the local dev loop to a cloud service |

## 4. Make the consequences concrete

Name what becomes easier, what becomes harder, and what this forecloses. Vague
consequences ("this improves maintainability") are the part a future reader most
needs and least often gets.

> Jobs are visible in the same database as the data they touch, so debugging is one
> query. In exchange, throughput is capped by the primary's write capacity, and we
> will need a different answer above roughly 500 jobs per second.

## 5. State reversibility

Say plainly whether the decision is cheap or expensive to reverse, and what
reversing costs. Reviewers weigh an easily-reversed decision differently, and
saying so shortens the review.

## 6. What bloats these

- Background sections explaining the domain to people who work in it daily.
- A scoring matrix over criteria that did not actually drive the decision.
- Consensus narrative — "after discussion, the team felt that…".
- Hedging on the decision itself. A record that does not decide is a proposal.
- Restating the problem in three sections under three different headings.

## 7. Write a decision as decided

If it is settled, write it as settled. If it is not, label the document a proposal
and name explicitly what would settle it — the experiment to run, the number to
measure, the person to ask. "We are leaning towards X" leaves the next reader with
your uncertainty and none of your context.

## 8. Never rewrite a superseded record

A decision record is a historical document. When the decision changes, write a new
record and link the old one forward. Editing the original destroys the reason the
format exists.
