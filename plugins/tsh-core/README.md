# TSH Core

Tool mechanics every TSH engineer needs regardless of discipline or stack.

This is a **core** plugin — the third family, alongside disciplines and stacks.
Install it at `user` scope, like a discipline plugin: what's in here depends on
neither your role nor the language a repo is written in, so it should follow you
everywhere. Stack plugins (`tsh-stack-frontend` and friends) go at `project`
scope instead, because the repo is what decides those.

`tsh-core` is deliberately small. There is no cap on how many skills it holds, but
the admission bar here is the highest in the repo and every addition discloses what
it costs. Read [Scope](#scope) before adding anything.

## Install

```shell
/plugin marketplace add TheSoftwareHouse/agentic-collections
/plugin install tsh-core@tsh-agentic-collections
```

## What's in it

| Skill | Invoke | Covers |
| :-- | :-- | :-- |
| `managing-git-worktrees` | `/tsh-core:managing-git-worktrees` | Git worktree lifecycle: create from a freshly fetched base branch on `origin` — any branch, defaulting to origin's own default — list read-only, remove one precisely identified target, each with explicit confirmation and post-mutation verification |
| `writing-technical-documents` | `/tsh-core:writing-technical-documents` | The house writing standard for any technical document — README, CHANGELOG, ADR, PR description, runbook, ticket, bug report, test plan: lead with the conclusion, verify every claim against the source, cut what does not change the reader's decision |
| `authoring-claude-extensions` | `/tsh-core:authoring-claude-extensions` | Which Claude Code extension a need calls for — skill, subagent, hook or plugin — and how to write it. Routes on *when* the guidance is needed, not just what it is about, because that is the distinction that decides whether an extension ever loads |
| `managing-claude-context` | `/tsh-core:managing-claude-context` | The project-context files Claude Code loads — root and nested `CLAUDE.md`, path-scoped rules in `.claude/rules/`, and a decision-record index: put each convention in the layer that actually loads it, keep every memory file thin and true, and audit the ones that have drifted |
| `managing-decision-records` | `/tsh-core:managing-decision-records` | The shape and lifecycle of an ADR — the four-section format, the status vocabulary, numbering, superseding, and keeping the index in step. Only `Accepted` records bind; every other status is history you read but never obey |
| `init` | `/tsh-core:init` | One-shot project setup: audits what already loads, then creates or repairs root and nested `CLAUDE.md`, path-scoped rules and the decision-record index by running the owning skills in order, and wires maintenance pointers into `CLAUDE.md` so future sessions keep it all current. Safe to re-run — the second pass is a repair |
| `session-dump` | `/tsh-core:session-dump` | Packages one session into a portable, redacted Markdown file a teammate can hand to whoever maintains the plugin that misbehaved — the conversation, the plugin versions in play, the tool failures, and nothing that matched a secret shape. It writes the file and stops; sending it is the sender's decision |
| `retro` | `/tsh-core:retro` | A retrospective over the session you are in: finds the friction that should have been tooling — a procedure reconstructed twice, a convention Claude was corrected on repeatedly, a side task that flooded the context — and writes the candidates to a proposal file with their quoted evidence, trigger, primitive and target. Proposes only; builds nothing |

`authoring-claude-extensions` and `managing-claude-context` split cleanly:
**"I want to build something"** goes to the first, **"I want this repo's memory files
to be right"** to the second. The first owns skills, subagents, hooks and plugins; the
second owns `CLAUDE.md`, `.claude/rules/` and the decision index. Each hands off to the
other rather than overlapping.

`retro` and `authoring-claude-extensions` are two halves of one job, split by which
question you are asking. **"What should we build?"** goes to `retro`, which analyses a
session and produces a proposal document. **"How do I build it?"** goes to
`authoring-claude-extensions`, which decides the primitive and writes the file. `retro`
loads that skill's routing table rather than restating it, and it never creates an
artifact — a retro's entire output is one Markdown file for a human to review. Like
`init`, it is deliberately not model-invocable, so "should this be a skill or a hook?"
still routes to `authoring-claude-extensions` and never to it.

`retro` and `session-dump` both read a session and neither changes anything but the one
file they write. They split on **whose problem it is**. `retro` asks *what should we
build?* over your own session, and produces a proposal for your own repository.
`session-dump` asks *how do I show someone else what broke?* and produces an artifact
that leaves the machine — which is why it, alone in this plugin, redacts, discloses what
it removed, and stops before sending.

`writing-technical-documents` governs prose craft and never an artifact's
structure. It will not tell you what sections a user story needs — that belongs to
the discipline skill that owns the artifact — only how to write the words inside
whatever shape the artifact already has.

`managing-claude-context` records conventions a team already holds; it does not
decide what a convention should be, and it asks rather than inventing one when the
codebase is ambiguous.

`init` and `managing-claude-context` do not compete: `init` is the **user command**
you type once per repository, and it works by running `managing-claude-context` and
its neighbours in order and wiring the result together. It owns only the sequence
and the maintenance pointers it leaves in `CLAUDE.md`; every rule about the
artifacts stays with the owning skill. It is deliberately not model-invocable, so
setup requests phrased in prose route to `managing-claude-context`, never to it.

Decision records are split three ways, deliberately — the verbs tell you which skill
you want:

| Concern | Skill |
| :-- | :-- |
| Index schema, the binding note, the `CLAUDE.md` pointer | `managing-claude-context` |
| Record format, sections, numbering, status lifecycle, superseding | `managing-decision-records` |
| The prose inside a record | `writing-technical-documents` |

None of them sets a record's status. Marking something `Accepted` asserts what a
team agreed, so it stays a human call — the skills propose one and name who decides.

Name a base branch and it is used; name none and origin's default branch is read
from the remote, so `main`, `master` and `develop` trunks all work. A base that
cannot be resolved stops the run — the skill never guesses one.

See [`CHANGELOG.md`](CHANGELOG.md) for what changed in each version. Updates arrive
with `/plugin update`.

Every skill here except `init`, `retro` and `session-dump` is model-invocable — Claude
loads it when the work matches its description, so you don't have to remember to type
the command. Those three are the deliberate exceptions
(`disable-model-invocation: true`): they are commands you type, their descriptions are
never preloaded, and they cost no routing budget. Between them they add eight skills'
worth of capability for five skills' worth of listing.

They keep a short `SKILL.md` and push detail into `references/`, loaded only when
the task needs it. The **"Load when"** column in the Reference Loading table is
what routes the model to the right file; keep it filled in when adding references.

### Using retro

`/tsh-core:retro` reads a session back and writes **one file** —
`docs/extension-proposals/<date>-<slug>.md` — listing the friction that should have been
tooling. Nothing else on disk changes. It never builds what it proposes.

Run it at the **end** of a session that felt repetitive, or one where Claude had to be
corrected more than once. Running it mid-task gives it half a session to work from.
Running it in a fresh one gets you a question, not a retro: there is nothing to analyse
yet, and it will ask which session you meant rather than guess.

```
/tsh-core:retro
/tsh-core:retro the worktree cleanup thread
/tsh-core:retro yesterday's work in the main checkout
```

The first analyses the whole conversation. The second narrows detection to one thread
and records that the retro was partial by instruction. The third reaches for a
**transcript** — a bundled script lists the sessions attached to this repository,
including every Git worktree, and digests the one you pick down to its user turns,
corrections and repeated steps. That path also covers a session long enough to have been
compacted, where the original wording is gone from context but survives on disk.

Each surviving candidate arrives with the evidence behind it:

```markdown
## P1 — Enforce the marketplace version bump before a plugin commit

- **Primitive:** hook · **Confidence:** strong
- **Target:** `.claude/settings.json` — repo-local
- **Handoff:** `/tsh-core:authoring-claude-extensions`

**Evidence** — 3 occurrences
1. "you forgot the version bump again", after the second plugin commit
...
**Trigger** — any commit touching `plugins/` without a `plugin.json` change
**Rejected alternative** — a `CLAUDE.md` line, because it already says this and was
still missed twice
```

**Getting the most out of it**

- Name a focus when the session did several unrelated things. One retro over three
  subjects finds less than three prompts would.
- Expect **"no candidates"** on a short, clean session, and read it as the skill
  working. A retro that always finds something is one nobody trusts twice.
- The output is a proposal for a person to weigh, not a decision. Once you agree with
  one, `/tsh-core:authoring-claude-extensions` builds it.
- Rejected candidates are listed with their reasons, so you can disagree with the
  judgement rather than just the conclusion.

**What it will not do:** create or enable any skill, agent, hook or MCP server; edit
`CLAUDE.md` or a `.claude/rules/` file; commit; or open a pull request.

Reading a transcript runs `node` through Bash, so the first time you use the third form
Claude will ask you to approve it. If you decline — or there is no `node` on `PATH` — the
retro falls back to the conversation in context and says so under **Not analysed** in the
file. That line is expected behaviour, not a broken install. It will not go looking for
another way in; a retro that spends its run on transcript access produces no proposal at
all.

### Using session-dump

`/tsh-core:session-dump` is for the other direction: a plugin **you did not write**
misbehaved, and the maintainer needs to see it. It writes **one file** —
`session-dumps/<date>-<slug>.dump.md` — and then stops. It does not send it, post it,
commit it, attach it, or tell you what went wrong.

```
/tsh-core:session-dump
/tsh-core:session-dump the code review that skipped the tests
```

You will be asked two questions before anything runs — *what were you trying to do*, and
*what did Claude do instead*. Your own words go into the file verbatim and are the first
thing the maintainer reads; they cannot be recovered from a transcript at any price. Then
you pick the session from a list that spans **every Git worktree attached to the
repository**, so a session from the main checkout is reachable from inside one.

What lands in the file:

| Section | Why the maintainer needs it |
| :-- | :-- |
| Sender report | Your account of the problem — the only part no tool can reconstruct |
| Provenance | Repository, branch, Claude Code version, model, permission mode, whether the session was compacted |
| TSH plugins | Every installed `tsh-*` plugin with version, scope and commit — plus the versions the transcript shows were *actually loaded*, which wins when the two disagree |
| Extension activity | Skills invoked, slash commands typed, subagents spawned, MCP tools used |
| Friction signals | Repeated tool calls, tool failures with their error text, permission denials, likely corrections |
| Conversation | Numbered user turns with Claude's reply and the tools it reached for |

**Never in it:** successful tool output, file contents, diffs or attachments. A dump is
bounded on purpose, and the file declares everything it left out, including any turns cut
to fit.

**Read it before you send it.** Values matching known secret shapes — API keys, tokens,
JWTs, private-key blocks, `user:password@host` URLs, `SOMETHING_SECRET=` assignments — are
replaced before anything reaches disk, and the file counts what it replaced. That is a
floor, not a guarantee: pattern matching cannot catch a password typed as prose, an
internal hostname, or a client's name. Placeholders like `API_KEY=${MY_VAR}` are left
alone deliberately, because an unset variable is very often the actual bug.

**Two things to do afterwards.** Add `session-dumps/` to your `.gitignore` — a dump is a
transcript sitting in a working tree, one `git add -A` from a commit — and delete the file
once it has been sent.

**Check the version first.** The dump names the plugin versions you have installed. If
yours is behind, `/plugin update` is a cheaper first move than a dump, and an
already-fixed bug costs a maintainer a day to rediscover.

**Some sessions should not be packaged at all**, and the skill will say so rather than
produce a smaller dump as a compromise: a client agreement that covers repository
contents, a session whose substance *is* the confidential material, or a sender who does
not want to read the file. The fallback is usually enough — describe the problem, name the
plugin and version, paste the one error message.

Like `retro`, it reads the transcript by running `node` through Bash, so the first use
prompts for approval. It makes at most two invocations — one to list, one to write — and
on failure reports the one-line reason and stops. It will not improvise another route to
your `.jsonl`; every alternative produces an unredacted file, which is the outcome the
whole command exists to prevent.

### The Atlassian connector

**This plugin bundles one MCP server** (`.mcp.json`): Atlassian's official
[Rovo MCP server](https://support.atlassian.com/atlassian-rovo-mcp-server/docs/getting-started-with-the-atlassian-remote-mcp-server/),
so Claude reads and updates Jira work items and Confluence pages directly instead of
waiting for someone to paste a ticket into the conversation. It sits here rather than
in a discipline plugin because Jira is not one job's tool — engineering, product
management and testing all read from it, and none of that changes with the language a
repo is written in.

**One step per machine.** Run `/mcp`, pick `atlassian`, finish the browser login. The
server is remote and OAuth-authenticated, so every call runs as you — it grants
nothing you could not already open in Jira yourself. Atlassian Cloud only. It appears
in `/mcp` as plugin-provided; disable it per project from the same panel. The cost is
not routing budget: an MCP server adds nothing to the skill listing, and Claude Code
defers tool schemas until a tool is used, so a session that never touches Jira pays
only for the tool names.

**Bitbucket is possible, but not bundled.** The same server does expose Bitbucket
Cloud (and Jira Service Management) — but only under API-token authentication, never
OAuth. That path needs an Atlassian org admin to enable API-token auth under **Admin
Hub → Rovo → Rovo MCP server**, the Bitbucket workspace linked to the organisation,
and a scoped token per person, so bundling it would ship a server that fails for most
installs. If you want it, add your own alongside:

```shell
claude mcp add --transport http atlassian-bitbucket https://mcp.atlassian.com/v1/mcp \
  --header "Authorization: Basic $(printf '%s' 'you@tsh.io:YOUR_SCOPED_TOKEN' | base64)"
```

That one covers Jira as well, so disable the bundled `atlassian` entry in `/mcp` if
you go this route — otherwise both sets of tools sit in the session.

## Scope

Every other plugin in this marketplace has a claimant and an affirmative question
— *is this QA's job?*, *is this TypeScript?*. `tsh-core` is the only one defined by
a **negation**: it holds what is neither. Negatively-defined containers accrete by
default, so the boundary has to be written down and enforced.

### Which family does a contribution belong to?

Ask in order and stop at the first yes:

1. Would this guidance change if the repo switched language or framework?
   → `tsh-stack-<stack-name>`
2. Would it change if the reader switched job? → the `tsh-<discipline>` plugin
   that owns the **outcome**
3. Neither, *and* it clears the admission bar below? → `tsh-core`

**Ties go to a discipline plugin. `tsh-core` is never the default answer.**

### The admission bar

- **Generic is not core.** Core skills are *tool mechanics* — the procedure is
  dictated by the tool's own semantics (`git`, `gh`, the shell), not by TSH's
  opinion about how to work. "Write good commit messages" is generic, applies to
  everyone, and is still a **discipline** skill, because only TSH's opinion could
  produce it. **If you cannot name the tool the skill wraps, it is not core.**
- **Two named exceptions, and the list is closed.** `writing-technical-documents`
  wraps no tool; it is admitted because every discipline's written deliverables are
  judged by it. `managing-decision-records` wraps no tool either; it is admitted for
  ADR format and lifecycle only, because `managing-claude-context` already mandates
  the decision index and status vocabulary, and splitting one artifact system across
  two install units would leave a `tsh-core` installer told to keep an index with no
  guidance on what a record is. Both are named here rather than generalised into an
  "output standards" or "artifact conventions" category — an exception you can point
  at is auditable, a category is a hole. `managing-decision-records` is the **last**
  artifact-convention skill admitted; a third makes it a category. Commit-message
  and PR-title conventions sit outside both and stay discipline skills.
  `managing-claude-context` is **not** an exception — it passes the test, naming
  Claude Code's own memory subsystem, whose loading mechanics dictate the whole
  procedure.
- **Evidence, not assertion.** Your PR names which **three of the five
  disciplines** would invoke the skill in a normal month. "It's generic" is not
  evidence.
- **No cap, but disclose the cost.** There is no maximum skill count. Your PR
  reports this plugin's **routing footprint** — the combined `name`, `description`
  and `when_to_use` characters across its skills — before and after, so the cost is
  visible when someone decides to pay it.

Why the bar is this high, and why footprint is the number that matters: everyone
installs this plugin, so every skill here costs every teammate context budget.
Claude Code preloads each installed skill's name and description to route on them,
truncates `description` + `when_to_use` at 1,536 characters per skill, and cuts
descriptions when the whole listing overflows — degrading routing for *every* skill
in *every* plugin, including the good ones. A count of skills never measured that;
three terse skills can cost less than one verbose one.

Growth is not a reason to split into `tsh-core-*`. There is no `tsh-core-*`. When
this plugin feels heavy, re-home what should not have been admitted.

### The bar covers every component, not just skills

Everything above is phrased in terms of skills because until now that is all this
plugin held. It applies unchanged to an MCP server, an agent or a hook — what changes
is the cost being disclosed. A bundled MCP server adds **no** routing footprint: it
puts nothing in the skill listing. Its cost is tool names, which Claude Code defers
until a tool is used, so the deciding test is the third one — **name three of the five
disciplines that use it in a normal month**. A server one discipline uses stays in
that discipline's plugin, which is why the Playwright server a UI agent drives is not
here.

Duplication is not the escape hatch it looks like. Plugin-provided servers are
deduplicated by **endpoint**, so two plugins declaring the same URL do connect once —
but the surviving definition decides the `mcp__plugin_<plugin>_<server>__*` namespace,
and the winner tracks plugin load order, which nobody controls. One home per server.

### What does not belong here

| Not this | Goes to |
| :-- | :-- |
| Language or framework content | `tsh-stack-<stack-name>` |
| Role practice, methodology, ways of working | the owning `tsh-<discipline>` |
| Company policy, onboarding, handbook prose | a document — it isn't a skill |
| "Utilities", helper scripts, one-off automation | nowhere; keep it in the repo that needs it |
| Anything used by one team or one project | that project's own `.claude/` |

A worked example of the boundary: `tsh-pe-setting-up-worktrees` in the private
collections repo sounds like a natural companion to `managing-git-worktrees`, and
it does **not** belong here — it mutates `.env` files and Docker Compose services,
so it fails question 1 and routes to `tsh-platform-engineering` or a stack plugin.
When it lands there, it still must not be cross-linked from this plugin.

## Contributing

Add a skill as `skills/<skill-name>/SKILL.md`, with supporting detail in
`skills/<skill-name>/references/<topic>.md`. Start from
[`templates/SKILL.md`](../../templates/SKILL.md) and read
[`CLAUDE.md`](../../CLAUDE.md) for the conventions and the local test loop.

Shipping a change means bumping `version` in
[`.claude-plugin/plugin.json`](.claude-plugin/plugin.json) and adding a
[`CHANGELOG.md`](CHANGELOG.md) entry in the same commit — without the bump,
`/plugin update` tells teammates they are already up to date and your change never
reaches them. `CLAUDE.md` hard rule 3 has the patch/minor/major semantics.

Three rules that bite hardest here:

- **Name the tool in the skill name.** `managing-git-worktrees`, not
  `managing-worktrees`. It keeps the *name-the-tool* admission test visible in the
  directory listing, and it sharpens description routing — "worktree" alone
  collides with monorepo *workspaces*. `writing-technical-documents` names an
  artifact class instead, because it is the one admitted exception; its presence in
  the listing is not permission to skip the test.
- **Reference only files inside this plugin**, by relative path. A skill cannot
  reliably read another plugin's files, because that plugin may not be installed —
  and the failure is a silent dead link, not an error. That applies with extra
  force here: `tsh-core` is installed by people who have no other plugin at all.

Phrase a skill's boundaries as **capability statements** ("this skill does not
initialize environment files"), never as pointers to skills in other plugins. The
capability phrasing survives those skills being renamed, re-homed, or never ported
at all.
