# TSH Core

Tool mechanics every TSH engineer needs regardless of discipline or stack.

This is a **core** plugin — the third family, alongside disciplines and stacks.
Install it at `user` scope, like a discipline plugin: what's in here depends on
neither your role nor the language a repo is written in, so it should follow you
everywhere. Stack plugins (`tsh-stack-typescript` and friends) go at `project`
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

`writing-technical-documents` governs prose craft and never an artifact's
structure. It will not tell you what sections a user story needs — that belongs to
the discipline skill that owns the artifact — only how to write the words inside
whatever shape the artifact already has.

Name a base branch and it is used; name none and origin's default branch is read
from the remote, so `main`, `master` and `develop` trunks all work. A base that
cannot be resolved stops the run — the skill never guesses one.

See [`CHANGELOG.md`](CHANGELOG.md) for what changed in each version. Updates arrive
with `/plugin update`.

Both skills are model-invocable — Claude loads them when the work matches their
description, so you don't have to remember to type the command.

They keep a short `SKILL.md` and push detail into `references/`, loaded only when
the task needs it. The **"Load when"** column in the Reference Loading table is
what routes the model to the right file; keep it filled in when adding references.

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
- **One named exception, and only one.** `writing-technical-documents` wraps no
  tool. It is admitted because every discipline's written deliverables are judged
  by it, and it is named here rather than generalised into an "output standards"
  category — an exception you can point at is auditable, a category is a hole.
  Commit-message and PR-title conventions sit outside it and stay discipline
  skills.
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
