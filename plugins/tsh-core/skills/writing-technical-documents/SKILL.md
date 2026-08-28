---
name: writing-technical-documents
description: "Applies TSH's writing standard to any technical document — README, CHANGELOG, ADR, RFC, runbook, PR description, ticket, user story, bug report or test plan — so it leads with the conclusion, states only verified facts, and is short enough to be read. Use when writing or revising a document meant for other people, or when asked to tighten, shorten or clarify prose."
when_to_use: "Trigger on: writing or updating a README, CHANGELOG entry, /docs page, runbook, ADR, RFC, technical proposal, PR description, release note, migration guide, ticket, user story, acceptance criteria, bug report, test plan or incident report; or any request to shorten, tighten, clarify, de-bloat or improve the readability of written text."
---

# Writing Technical Documents

Produces technical documents people actually read: the conclusion first, every
claim verified, and nothing left in that does not earn its place. The craft rules
below are drawn from *Writing for Busy Readers* by Todd Rogers and Jessica
Lasky-Fink, restated as checkable rules rather than principles.

**This skill governs prose craft, never structure.** It does not decide what
sections an ADR needs or what a user story must contain. When an artifact already
has a required shape — from the repository, the tracker, or another TSH skill —
that shape wins, and this skill governs only the words inside it.

## When to Use

- Writing or updating a README, `/docs` page, runbook, or documentation-site page
- Writing a CHANGELOG entry, PR description, release note, or migration guide
- Writing an architecture decision record, RFC, or technical proposal
- Writing a ticket, user story, acceptance criteria, or bug report
- Writing a test plan, incident report, or postmortem
- Any request to shorten, tighten, or clarify text that already exists

## Applicability and Precedence

Read the repository's own documentation conventions first, and open one or two
sibling documents in the same directory before writing. Local conventions outrank
this skill's defaults. Apply these rules where the repo is silent, and record any
deliberate deviation rather than silently mixing conventions.

Where another skill or a tracker template defines an artifact's required sections,
follow it exactly and apply these rules only to the prose within those sections.

## Explicit Exclusions

This skill does not:

- define, propose, or produce the structure, template, or required sections of any
  artifact, even when asked for one directly — see
  [Requests This Skill Declines](#requests-this-skill-declines)
- write or edit product code, configuration logic, tests, or infrastructure
- govern commit subject lines or pull request titles — the repository's own commit
  convention owns those
- invent facts, examples, or rationale to fill an empty section
- rewrite historical CHANGELOG entries, decision records, or incident reports
- approve, review, or sign off on technical accuracy the source files do not show

When a document cannot be written correctly without a code change first, stop and
report the dependency instead of editing code.

## Non-negotiable Rules

| Severity | Rule |
| --- | --- |
| MUST | Put the conclusion, decision, or required action in the first sentence. Background comes after, or not at all. |
| MUST | Verify every path, command, flag, version, and link target against the source before writing it. |
| NEVER | Write a claim you have not confirmed. Omit it, or mark it explicitly as an open question. |
| NEVER | Link to a page that does not exist. A broken internal link is a failure, not a cosmetic issue. |
| MUST | Cut every word, sentence, and section that does not change what the reader thinks or does. |
| MUST | Keep one idea per paragraph, and prefer the shorter, plainer word. |
| MUST | Where the project has a domain dictionary, use its canonical terms — never a synonym or a translation you invent. |
| NEVER | Ship filler — "comprehensive", "robust", "seamless", "leverage", "in order to", "it should be noted", "simply", "just". |
| MUST | Use a table or list when the content is enumerable, prose when it is not. Never format for decoration. |
| MUST | Write headings that summarise what follows, so a reader skimming headings alone can navigate. |
| MUST | End with the reader's next action whenever one exists. |
| NEVER | Author, invent, or propose an artifact's structure, template, or required sections — **including when asked for one directly**. Decline as described below and offer the craft help instead. |
| NEVER | Change the structure of a document that already has one. |
| MUST | Run the revision pass in Step 5 before handing off. A first draft is never the deliverable. |

## Reference Loading

| Reference | Load when | Covers |
| --- | --- | --- |
| [Revision pass](./references/revision-pass.md) | A draft exists and is being tightened, shortened, or clarified | The mechanical cut list: filler phrases, hedges, dead openings, buried conclusions, and what to do about each |
| [Repository documentation](./references/repository-documentation.md) | Writing a README, `/docs` page, runbook, or documentation-site page | The reader who arrives with no context, the exists/use/next contract, path and command verification, site frontmatter and link gates |
| [Change records](./references/change-records.md) | Writing a CHANGELOG entry, PR description, release note, or migration guide | Leading with impact and required action, naming who is affected, describing breakage in the reader's terms |
| [Decision records](./references/decision-records.md) | Writing an ADR, RFC, or technical proposal | Decision before deliberation, compressing alternatives, making consequences and reversibility explicit |
| [Work items](./references/work-items.md) | Writing a ticket, user story, acceptance criteria, or bug report | The reader deciding whether to pick it up, cutting origin narrative, making "done" unambiguous, observed vs. expected |

## Procedure

**Step 1 — Name the artifact and the reader.** State which document type this is,
who reads it, and what decision they make after reading. If you cannot name the
decision, the document has no job — ask what it is for before writing. Check
whether the repository or another skill already defines this artifact's structure;
if so, follow it and apply these rules only within it.

**Step 2 — Load the matching reference.** Read the reference for this artifact
class **before writing the first sentence** — each one names what that reader
front-loads and what typically bloats that artifact, and neither is reconstructible
from the rules table alone.

**Step 3 — Gather and verify the facts.** Read the code, configuration, and
neighbouring documents. Confirm every path, command, flag, version, and link target
you intend to write. Do not document behaviour you have not confirmed.

**Step 4 — Draft conclusion-first.** Lead with the outcome, decision, or required
action. Add background only where the reader cannot act without it. Write short
sentences, one idea per paragraph, active voice.

**Step 5 — Run the revision pass.** Read
[`revision-pass.md`](./references/revision-pass.md) and apply it to the draft. This
step is mandatory and it is where most of the value is: the first draft states the
content, the revision pass makes it readable.

**Step 6 — Verify links and paths.** Confirm every internal link resolves and every
referenced path exists. For documentation-site changes, run the site build — broken
internal links fail it. Fix problems before handing off; never report an unverified
document as finished.

## Requests This Skill Declines

A request for a **template, a section list, or "what should a good X contain"** is
outside this skill, even when the artifact is one it otherwise writes. Do not
produce the template, and do not produce it with a caveat attached — a template
offered under a disclaimer is still a template, and it will be copied.

Respond by naming the boundary in one sentence, then offering what this skill does
have:

1. Say that this skill governs the prose inside an artifact, not its shape.
2. Ask for the structure the team already uses — a tracker template, a previous
   example, a repository convention — and offer to write within it.
3. Offer the craft help that is in scope: tightening an existing draft, making
   acceptance criteria checkable, front-loading a document that buries its point.

If TSH has no agreed structure for that artifact yet, say so plainly and note that
defining one belongs to the discipline that owns the artifact. Do not fill the gap
by inventing a structure here — that is the decision this skill exists not to make.

## Self-check Before Handoff

Answer each line before returning the document. Any "no" sends you back to Step 5.

```text
- [ ] The first sentence carries the conclusion, decision, or required action
- [ ] Every path, command, flag, and version was checked against the source
- [ ] Every internal link resolves
- [ ] No sentence survives that does not change what the reader thinks or does
- [ ] No banned filler remains
- [ ] Headings alone describe the document's shape
- [ ] The reader's next action is stated, or there genuinely is none
- [ ] The artifact's existing structure is unchanged
- [ ] No template or section list was authored
```
