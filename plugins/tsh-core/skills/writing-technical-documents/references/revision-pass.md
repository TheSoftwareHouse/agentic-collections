# Revision pass

Use this flow only when a draft already exists. Work top to bottom, one sweep per
section — trying to apply every rule at once produces a lightly-edited draft rather
than a revised one. Most of a document's readability is won here, not in drafting.

## 1. Move the conclusion to the front

Find the sentence that states what happened, what was decided, or what the reader
must do. In a first draft it is usually in the last paragraph of the section,
because that is the order you worked it out in. Move it to the first sentence and
delete the runway that led to it.

Apply this per section, not only to the document as a whole.

## 2. Delete dead openings

These carry no information. Cut the whole phrase and start at the next word:

- "This document describes…" / "In this section we will…"
- "As you may know…" / "As mentioned above…"
- "It is important to note that…" / "Please note that…"
- "There are several ways to…"
- "Before we begin, let's take a look at…"

## 3. Cut filler phrases

| Cut | Use |
| --- | --- |
| in order to | to |
| due to the fact that | because |
| at this point in time | now |
| in the event that | if |
| prior to / subsequent to | before / after |
| has the ability to | can |
| provide support for | support |
| make a decision | decide |
| a number of | several, or the actual number |
| with regard to | about |
| utilize / leverage | use |
| basically, essentially, actually, simply, just | delete |

## 4. Delete marketing adjectives

"Comprehensive", "robust", "seamless", "powerful", "cutting-edge", "best-in-class",
"easy", "intuitive", "blazing-fast". They are unverifiable, so readers discount
them — and they cost the sentence its credibility.

Replace each with the fact that made you reach for it. Not "blazing-fast queries"
but "p99 under 40 ms". Not "an easy migration" but "one command, no downtime". If
no such fact exists, the adjective was decoration and the sentence is better
without it.

## 5. Remove hedges that carry no information

"Probably", "generally", "in most cases", "it seems", "we think", "somewhat",
"fairly". Keep a hedge only when the uncertainty is real *and* the reader would act
differently because of it — then state the uncertainty precisely instead. "This may
be slow" is noise; "this is untested above 10k rows" is information.

## 6. Split paragraphs that turn

Any paragraph containing "however", "that said", or "on the other hand" usually
holds two ideas. Split at the turn. One idea per paragraph is what lets a reader
skip a paragraph safely, which is what they are going to do anyway.

## 7. Shorten sentences

For anything over roughly 25 words, look for a clause that can become its own
sentence. Reverse passive voice wherever the actor matters — "the config is loaded
at startup" hides who loads it and whether you can change it.

## 8. Convert enumerable prose into a table or list

If three or more items share a shape — name and meaning, option and default, step
and command, target and convention — they are a table. Prose that enumerates is the
most common form of unnecessary length, and it is the hardest form to scan.

## 9. Cut formatting that carries no information

- bold applied to whole paragraphs
- a nested list with a single child
- a heading over two sentences
- a table of contents on a page short enough to scan
- horizontal rules between every section
- emoji used as bullets

Formatting earns its place by helping the reader find or compare things. Anything
else competes with the content for attention.

## 10. Check the ending

Does the reader know what to do next? If an action exists, state it. If none does,
stop at the last informative sentence — do not add a summary that repeats the
document back to someone who just read it.

## Three rewrites

Where the rule alone is not enough to see the move:

**Buried conclusion**

> After investigating the timeout reports, we looked at the connection pool
> configuration and compared it against the load profile. It turns out the pool was
> sized for the old traffic pattern. We have increased it to 50.

> The connection pool is now 50, up from 10 — it was sized for pre-launch traffic,
> which is what caused the timeouts.

**Enumerating prose**

> The `--dry-run` flag previews changes without applying them, while `--force`
> skips confirmation prompts, and `--verbose` prints each step as it runs.

> | Flag | Effect |
> | --- | --- |
> | `--dry-run` | Preview changes without applying them |
> | `--force` | Skip confirmation prompts |
> | `--verbose` | Print each step as it runs |

**Unverifiable claim**

> We chose Postgres because it is a robust and powerful database with excellent
> support for our use case.

> We chose Postgres because we need transactional writes across three tables, which
> the previous document store could not guarantee.
