# Reading workshop materials

What each input type is good for, and how it fails.

## PDFs and documents (`Read`)

PDFs are read with the standard `Read` tool — there is no separate PDF server.

- Use it for client briefs, requirements documents, process descriptions,
  contracts, regulatory documents, and anything the user attaches or references.
- **Beyond 10 pages, pass an explicit `pages` range.** Work in chunks of ≤20 pages
  and summarize per chunk before merging.
- Treat PDF content with the same rigour as a transcript: requirements, decisions,
  constraints, business rules.
- **A scanned PDF with no text layer returns empty content.** Say so and ask for a
  text-based version. Never infer contents from a filename.
- Password-protected or corrupted file: report it and ask for an alternative.
- Cross-reference what you find against the transcript and designs, and surface
  conflicts rather than silently picking one.

**Unsupported formats.** Binary Office files (`.xlsx`, `.xlsm`, `.docx`, `.doc`)
cannot be read directly — ask for a PDF, CSV or plain-text export, and never assign
one to a worker. **Image files** (`.png`, `.jpg`, `.svg`) are not read
automatically: name the file and its location and ask whether it needs manual
review or is informational.

Skip `Read` entirely when the user already pasted the content into the
conversation.

## Figma and FigJam

Figma MCP is **not bundled with this plugin** — it is a prerequisite the session
supplies. Check whether Figma tools are connected before promising design analysis.

- Use them when the materials include Figma or FigJam links: user flows,
  wireframes, process diagrams, and the functional requirements a design implies —
  screens, interactions, states.
- Look for annotations, comments and flow lines; they usually carry the business
  logic.
- Check for features visible in a design but absent from the transcript. That gap
  is one of the most valuable things this phase finds.
- Focus on **what the system should do**, not how it looks. Extracting CSS values,
  pixel measurements or styling detail is out of scope for a backlog.
- **If blocked** — no URL, access denied, no Figma MCP connected, tool errors —
  stop and tell the user. Never skip design analysis silently.

## Structural reasoning

For genuinely load-bearing structural decisions — epic boundaries, conflicting
sources, dependency chains, whether to split or merge a story — think it through
before answering rather than deciding inline. If the user has not raised the
thinking budget and the decision is load-bearing, say that a deeper pass would help
and let them decide.
