---
name: processing-workshop-transcripts
description: "Cleans a raw workshop or meeting transcript into a structured, business-relevant document — small talk and filler removed, content grouped by discussion topic, with decisions, action items and open questions extracted. Use before any backlog extraction when the input is a raw transcript, meeting notes, or a recording export."
when_to_use: "Trigger on: a raw transcript or meeting notes handed over for processing, 'clean up this transcript', preparing workshop material for epic and story extraction, or a transcript PDF that needs structuring first."
---

# Processing Workshop Transcripts

Turns noisy discussion material into a document that later phases can rely on. It
removes greetings, filler and tangents while preserving every actionable and
business-critical point.

## Applicability and Precedence

If the project already has a transcript or meeting-notes convention, follow it and
apply this skill only where that convention is silent. Content preservation always
outranks tidiness: when in doubt about whether a passage is business-relevant,
**keep it**.

## Explicit Exclusions

This skill does not extract epics or stories, judge scope, or resolve
contradictions between sources. It produces one cleaned transcript and stops.

## Non-negotiable Rules

| Severity | Rule |
| --- | --- |
| MUST | Preserve every decision, commitment, constraint and open question, including ones stated in passing. |
| MUST | Keep the exact wording of requirements, constraints and conflicting viewpoints in a Preserved Context section, with attribution. |
| NEVER | Invent metadata, roles or decisions the source does not state. Record "not stated in source" instead. |
| NEVER | Infer the contents of a scanned PDF that returns no text. Report it and ask for a text-based version. |

## Reference Loading

| Reference | Load when | Covers |
| --- | --- | --- |
| [Cleaned transcript example](./references/cleaned-transcript-example.md) | Before writing the output file — always | The exact section order and table shapes of the deliverable |

## Execution Context

Running in the main conversation: ask the user for missing metadata and write the
file yourself. Running as the `transcript-cleaner` subagent: you have no
interactive and no write tool — return the structured transcript as your final
message and collect anything you would have asked under `## Open Questions`.

## Procedure

1. **Identify the format and metadata.** Speaker-labelled, plain notes, timestamped,
   mixed, or PDF. Read PDFs with the `Read` tool — no separate PDF server; pass an
   explicit `pages` range beyond 10 pages and work in chunks of ≤20. Capture date,
   duration (compute it from first and last timestamp), topic and context.
2. **Tag participants.** Name and role where stated or unambiguous from context.
   List a participant without a role rather than guessing one.
3. **Remove non-business content**: greetings and sign-offs, small talk, filler words
   and verbal tics, technical difficulties ("you're on mute"), off-topic tangents,
   and repeated restatements — keeping the clearest version of each point.
4. **Group by discussion topic.** Find the natural topic boundaries, give each a
   descriptive heading, list key points as bullets with speaker attribution where
   available, keep chronological order within a topic, and consolidate a topic that
   resurfaces later in the transcript under one heading.
5. **Extract key decisions** — explicit ("we agreed to…") and implicit (discussion
   converging without a formal declaration). Record what was decided, who made or
   endorsed it, and any conditions attached.
6. **Extract action items and open questions.** Action items: what, who, deadline.
   Open questions: anything raised and unanswered, deferred, or acknowledged as
   ambiguous.
7. **Preserve critical raw context.** Exact quotes where the original wording
   matters — requirements in specific business language, stakeholder constraints,
   conflicting viewpoints, domain terminology defined during the session.
8. **Write the file.** Follow
   [`cleaned-transcript-example.md`](./references/cleaned-transcript-example.md) and
   save to `specifications/<workshop-name>/cleaned-transcript.md`. Check before
   finishing: nothing business-relevant was dropped, topics are logically grouped,
   and decisions, action items and open questions are complete.

## Related Skills

- [`extracting-epics-and-stories`](../extracting-epics-and-stories/SKILL.md) — consumes
  the cleaned transcript as its primary input.
- [`analyzing-discovery-context`](../analyzing-discovery-context/SKILL.md) — synthesizes
  it with the other workshop materials.
