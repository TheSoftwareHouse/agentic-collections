---
name: domain-dictionary
description: "Entry point for producing, reviewing and maintaining a per-product domain dictionary — the canonical business-term glossary, not domain-driven design. Run /tsh-product-management:domain-dictionary with a project name, a workshop directory of transcripts, PDFs or designs, a repository path to reconcile against, or nothing."
disable-model-invocation: true
---

# Domain dictionary

Target: **$ARGUMENTS**

If nothing was supplied, ask what to work on before doing anything else — a project
name, a workshop directory of transcripts, PDFs or designs, or a repository path to
reconcile terms against.

## What this runs

**Invoke `/tsh-product-management:managing-domain-dictionaries`** and follow it end to
end. It owns the three modes, the elicitation protocol, the review passes and the
handoff.

Invoke the skill — do not simply `Read` its `SKILL.md`. Reading the file gets you the
text; invoking it is what puts the skill's own configuration into effect for the
session.

## Which mode starts

| What was supplied | Mode that starts |
| --- | --- |
| Nothing on disk for the project | Interview |
| Transcripts, PDFs, designs or an existing backlog | Harvest |
| A codebase path | Reconcile |

On a live project the modes compose in order: Harvest, then Reconcile, then Interview
for whatever is still missing.

## Before you start

Check what this session actually has connected, and say so up front rather than
discovering it at the handoff:

- **Figma MCP** — needed when Harvest reads design material.
- **Atlassian MCP** — needed only if the handoff menu's Confluence option is chosen;
  committing into a repository or handing the file over directly need neither server.

## What you should end up with

- `specifications/projects/<project-name>/domain-dictionary.md` — the source of truth,
  outlives the session
- `specifications/projects/<project-name>/.dictionary-gates.md` — the gate ledger
  (`D1`–`D3`)
- `specifications/<workshop-name>/.dictionary-delta.md` — this session's proposal,
  merged into the project file only after approval
- `docs/domain-dictionary.md` (default) — the projection in the adopting repository,
  written on the `/tsh-core:managing-claude-context` side of the handoff
