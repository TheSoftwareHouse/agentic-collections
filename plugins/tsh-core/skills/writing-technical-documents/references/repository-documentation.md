# Repository documentation

Use this flow for README files, in-repo `/docs` pages, runbooks, and
documentation-site pages. It covers how the craft rules land on these documents —
not what sections they must contain.

## 1. Who the reader is

Someone who arrived from a search result or a link, mid-task, with no context and
no patience. They are deciding whether this is the right page. You get the first
two sentences to answer that; after them the reader is either committed or gone.

They are not reading to learn the domain. They already know what Docker is and what
a REST API is. They need the part that is specific to *this* repository.

## 2. The contract every page owes

Three things, in this order:

1. **What this is, and why it exists** — one or two sentences, no marketing.
2. **What to do with it** — the commands and paths, verified.
3. **Where to go next** — the following step, or the page that has it.

Anything serving none of these is a deletion candidate. Run that test on every
section before you keep it.

## 3. What bloats these documents

- Project history in a README — "this service was extracted from the monolith
  in 2022 because…". That is a decision record, or it is nothing.
- Explaining general concepts the reader already knows.
- Prerequisites nobody on the team lacks.
- A table of contents on a page short enough to scan.
- Boilerplate duplicated from an org-level file instead of linked.
- A "Features" list that restates the headings below it.

## 4. Front-loading a README

The first line says what this is, in one sentence. The next thing on the page is
how to run it. Everything else — configuration, architecture, contributing — comes
after, because a reader who cannot start does not care about any of it.

Resist opening with a paragraph of context. If the reader needs context to run the
thing, put it in the sentence that tells them to run it.

## 5. Match the neighbours

Open one or two sibling pages in the same directory before writing, and mirror
their heading order, frontmatter fields, link style, and section naming. A page
that is individually better but structurally different makes the set harder to use.
Consistency across a docs set beats any single page's stylistic improvement.

## 6. Verify everything executable

Every command in a README is a promise. Read it out of the source — `package.json`
scripts, the Makefile, the CI config — rather than from memory or from the previous
version of the page, which may already be wrong.

- Commands: confirmed against the script or CI definition that defines them
- Paths: confirmed to exist
- Flags: confirmed against the tool's own help output
- Versions: read from the manifest, never recalled

A command that no longer works costs the reader more than the page saved them.

## 7. Documentation-site pages

Use the frontmatter fields the site's existing pages use — commonly
`sidebar_position` and `title`. Read a neighbouring page rather than assuming.

Internal links must resolve, because the site build fails on broken ones. Never
invent a link to a page you are not creating in the same change; use plain code
formatting or an existing valid link instead. Run the build before handing off.

## 8. Runbooks

The reader is under pressure and possibly half awake. That changes the writing:

- Numbered steps, one action per step, in the order performed.
- The exact command, copy-pasteable, with no placeholder the reader must guess.
- The expected output after each step, so they can tell it worked.
- What to do when the output does not match — including "stop and escalate".
- No prose paragraphs between steps. Context goes at the top or in a footnote.

State the entry condition at the top: what symptom means this runbook applies. A
runbook a reader cannot confirm is the right one is a runbook they will not follow.
