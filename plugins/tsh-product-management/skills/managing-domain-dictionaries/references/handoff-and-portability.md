# Handoff and portability

A dictionary is written once but read in places this skill never runs — a
repository's `CLAUDE.md`, a code review, an onboarding doc. This reference
covers how the file leaves the product-management workspace and stays
usable once it has.

## Transport is the user's call

Product managers routinely work in local-only repositories; many projects
have no Confluence at all. The skill prescribes no transport. The
obligation is on the *artifact*, not on a pipeline: a dictionary that
depends on how it was delivered breaks the moment it is delivered a
different way.

## Self-describing: the provenance header

The header defined in
[`dictionary-format.md`](./dictionary-format.md#header--language-policy)
carries a **Provenance** field — source project, version, date, and what it
was last reconciled against. That field is what makes a travelled copy
diffable against its source with **no link home**: a dictionary sitting in
a product repository, months after the session that produced it, still
states where it came from and how current it was when it left. Without it,
a copy in a repository is an orphan — nobody downstream can tell whether it
is a week or a year behind the source.

Update Provenance on every export, not only on every edit. A copy handed
off unchanged since the last reconcile still needs its date refreshed, or
the diffability the header exists for is lost on day one.

## Independent of the workspace layout

The file depends on nothing in the product-management workspace: no
relative path back to `specifications/projects/<project-name>/`, no
reference to `.dictionary-delta.md`, `.dictionary-gates.md` or any other
working file this skill uses while building it. Everything a reader needs
is inside the dictionary itself — the header, the term table, and the
sections around it. Dropping the file into any repository, on its own,
works.

This is what makes the adopting side possible without coupling to this
skill: repository adoption is `/tsh-core:managing-claude-context`, and it
is source-agnostic by design — its job is to wire up whatever dictionary
file is present, however it arrived. It does not know or care that
`managing-domain-dictionaries` produced it.

## The handoff menu

Close a dictionary session by presenting three options, **with none named
as the default** — the right one depends on the repository and the client,
not on this skill:

| Option | What happens |
| --- | --- |
| Commit into the product repositories | The file lands at the path `/tsh-core:managing-claude-context` expects (default `docs/domain-dictionary.md`) and travels with the code from then on |
| Publish to Confluence | Only when the Atlassian server is connected; the dictionary becomes a page the client and team can both read, alongside — not instead of — a committed copy |
| Hand the file over directly | The plain Markdown file, handed to whoever asked for it, with no further action from this skill |

Present all three every time. Naming one as the default would substitute
this skill's judgment for the user's, and the right choice depends on
context this skill does not have — whether Confluence is even connected,
whether the repository exists yet, who is asking.

## No secrets, no personal data

A dictionary travels into repositories and is committed. **No client secrets and
no personal data go in a dictionary.**
Nothing here is a place to record an API key, a credential, a named
individual's contact details, or anything else that should not sit in
version control next to the code. If a workshop surfaces something like
that, it stays out of the term table entirely — it is not a term, and no
disposition in this skill applies to it.
