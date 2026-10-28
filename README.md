# TSH Agentic Collections

A [Claude Code](https://code.claude.com/docs) plugin marketplace for The Software
House, carrying custom agents and skills you can install into any project. It
publishes three families:

- **Core** (`tsh-core`) — *the ground under both*. One small plugin of tool
  mechanics that depend on neither your role nor the repo. Install it; it's for
  everyone.
- **Disciplines** (`tsh-product-engineering` and friends) — *how we work*. One per
  discipline. Install the one that matches your job.
- **Stacks** (`tsh-stack-frontend` and friends) — *what we work with*. One per
  technology stack. Install the ones a given project is built on.

> **Heads up:** one discipline plugin, `tsh-product-design`, is still an **empty
> scaffold**. Installing it works and is worth doing now — you'll pick up agents and
> skills automatically as we land them — but it contributes no components yet, so an
> empty component list after installing it is expected, not a broken install.
> **Every other plugin ships real skills today.**

Requires Claude Code v2.1 or newer:

```shell
claude --version
```

If you need to update: `npm install -g @anthropic-ai/claude-code@latest`, or
`brew upgrade claude-code` if you installed it with Homebrew.

## Step 1 — add the marketplace

Run this inside any Claude Code session. It registers the catalog so you can browse
it; nothing is installed yet.

```shell
/plugin marketplace add TheSoftwareHouse/agentic-collections
```

This repo is private, so your git needs to be able to clone it — a working SSH key
or `gh auth login` already set up. Alternatives if the `owner/repo` shorthand fails:

```shell
/plugin marketplace add git@github.com:TheSoftwareHouse/agentic-collections.git
/plugin marketplace add https://github.com/TheSoftwareHouse/agentic-collections.git
/plugin marketplace add https://github.com/TheSoftwareHouse/agentic-collections.git#some-branch
/plugin marketplace add ./agentic-collections        # from a local clone
```

The catalog is registered for **you, in every project** by default. It takes a scope of
its own — run this from a repo's root to register it for that repo only:

```shell
claude plugin marketplace add TheSoftwareHouse/agentic-collections --scope project
```

`--scope` takes `user`, `project` or `local`, and means the same thing here as it does
for plugins in Step 2.

## Step 2 — install the plugins you want

Copy just the lines you need:

```shell
# Core — everyone
/plugin install tsh-core@tsh-agentic-collections

# Disciplines — pick the one that matches your job
/plugin install tsh-product-engineering@tsh-agentic-collections
/plugin install tsh-product-testing@tsh-agentic-collections
/plugin install tsh-product-management@tsh-agentic-collections
/plugin install tsh-product-design@tsh-agentic-collections
/plugin install tsh-platform-engineering@tsh-agentic-collections

# Stacks — pick what the project is built on
/plugin install tsh-stack-frontend@tsh-agentic-collections
/plugin install tsh-stack-nodejs@tsh-agentic-collections
/plugin install tsh-stack-serverless@tsh-agentic-collections
/plugin install tsh-stack-python@tsh-agentic-collections
/plugin install tsh-stack-aws@tsh-agentic-collections
/plugin install tsh-stack-gcp@tsh-agentic-collections
/plugin install tsh-stack-azure@tsh-agentic-collections
```

Each install asks you to pick a **scope**:

| Scope | Who gets it | Where it's written |
| :-- | :-- | :-- |
| **User** | You, in every project | your user settings |
| **Project** | Everyone working on this repo | the repo's `.claude/settings.json` — **committed**, so it travels with the repo |
| **Local** | You, in this repo only | `.claude/settings.local.json` — keep it out of git |

Pick **User** if you're installing for yourself. Pick **Project** to give a whole
team the plugin via the repo. Pick **Local** to try one out in a single repo without
committing anything.

The three plugin families usually want different answers, and it's worth being
deliberate about it:

- **Core travels with you** — **User** scope, same as your discipline plugin. It
  depends on neither your role nor the repo, so it should follow you everywhere.
- **Discipline plugins travel with you** — **User** scope. Your job doesn't change
  from repo to repo.
- **Stack plugins travel with the repo** — **Project** scope. The repo already
  knows what it's written in, so everyone working on it should get the same
  guidance, and nobody should carry another stack's skills around.

Prefer the shell (for onboarding scripts, or to skip the interactive prompt):

```shell
claude plugin install tsh-product-testing@tsh-agentic-collections --scope user
claude plugin install tsh-product-testing@tsh-agentic-collections --scope project
claude plugin install tsh-product-testing@tsh-agentic-collections --scope local
```

Three things the table doesn't say:

- **Scope is resolved against your current directory.** Run `project` and `local`
  installs from the target repo's root, not from wherever your session started.
- **To confine a plugin to one project, scope both.** The marketplace has its own
  scope (Step 1). Scope only the install and you've still registered the catalog
  everywhere.
- **Scopes stack.** A committed project set is a starting point, not a cage —
  anyone can add their own plugins on top at `user` or `local` scope, and both
  sets load together.

`local` scope is only private if you keep the file out of git; nothing adds it for
you. Add `.claude/settings.local.json` to your `.gitignore` — [this repo's
`.gitignore`](.gitignore) does exactly that.

Installing never copies plugin files into your project. Everything lives in
`~/.claude/plugins/marketplaces/`, whatever the scope — scope decides which projects
load a plugin, not where it's stored.

You can also browse instead of typing names: run `/plugin`, go to the **Discover**
tab, and press Enter on a plugin to see its details and install it.

## Step 3 — activate

Read the install summary:

- `Plugin is now active.` → you're done.
- `Run /reload-plugins to activate.` → run that command:

```shell
/reload-plugins
```

If it warns that reloading will re-read the conversation, rerun it as
`/reload-plugins --force`. The reload summary counts only `commands/` directories,
so `0 skills` is normal and doesn't mean anything failed.

## Step 4 — sign in to Jira and Figma, once per machine

`tsh-core` bundles two MCP servers: the Atlassian one, so Claude reads and updates
Jira work items and Confluence pages directly, and the Figma one, so it reads designs
— layout, variables, components and a rendered export — instead of working from a
description. Both need one interactive login each:

```shell
/mcp
```

Pick `atlassian`, finish the browser sign-in, then do the same for `figma`. You're
done — on this machine, for every project. Every call then runs under your own
account and grants nothing you could not already open in Jira or Figma yourself.
Atlassian Cloud only; Figma works on all seats and plans. Skip either and that server
simply shows as needing authentication; nothing else breaks, though the UI
verification gate in `tsh-product-engineering` will report `VERIFICATION NOT RUN`
rather than judging a design it cannot read.

Two things deliberately left out, both documented in
[`plugins/tsh-core/README.md`](plugins/tsh-core/README.md) with an opt-in command:
**Bitbucket**, because the Atlassian server covers it only under API-token
authentication that needs an org admin to enable first, and **Figma's desktop
server**, because it is a separate local endpoint that fails for anyone not running
the desktop app and needs a Dev or Full seat on a paid plan.

## Using what you installed

Skills and agents are invoked differently, and both are namespaced by plugin:

```shell
/tsh-product-testing:<skill-name>     # skills — type / and the plugin name
@tsh-product-testing:<agent-name>     # agents — @-mention typeahead
```

To see exactly what a plugin gives you, run `/plugin`, open the **Installed** tab,
and press Enter on it. Same list from the shell:

```shell
claude plugin details tsh-product-testing@tsh-agentic-collections
```

## Onboarding a whole project team at once

Installing at `--scope project` already does this — it writes your project's
`.claude/settings.json` for you, in exactly the shape below. Commit that file and your
team has the set.

Write it by hand instead when you want to declare the set *before* anyone installs
anything: a repo template, or an onboarding PR that lands the plugin list alongside the
code. Everyone who trusts the folder gets prompted to install the marketplace and the
listed plugins:

```json
{
  "extraKnownMarketplaces": {
    "tsh-agentic-collections": {
      "source": {
        "source": "github",
        "repo": "TheSoftwareHouse/agentic-collections"
      }
    }
  },
  "enabledPlugins": {
    "tsh-product-engineering@tsh-agentic-collections": true,
    "tsh-product-testing@tsh-agentic-collections": true,
    "tsh-stack-frontend@tsh-agentic-collections": true,
    "tsh-stack-nodejs@tsh-agentic-collections": true
  }
}
```

The stack plugins are the clearest case for committing this file: a repo's runtime
targets are the same for everyone who clones it. List only the ones that apply —
a backend-only service has no use for the frontend plugin.

`tsh-core` is deliberately **not** in that list, and that isn't an oversight to
fix. It's user-scope by design — it follows the person, not the repo — so pinning
it here would mean every repo in the company re-declaring the same line, and
anyone who already installed it getting a redundant prompt. The discipline plugins
are listed only because a repo may want to hand a new team a sensible starting
set; drop them if your team installs their own.

Teammates still need to complete the install prompt the first time — a plugin from
an external source doesn't load until it's actually installed. Until then Claude
Code reports it as not installed and prints the `claude plugin install` command.

## Staying current

```shell
/plugin marketplace update tsh-agentic-collections   # refresh the catalog
/plugin list                                         # what you have installed
```

Third-party marketplaces have **auto-update off by default**. To turn it on: run
`/plugin` → **Marketplaces** → select `tsh-agentic-collections` → **Enable
auto-update**.

The two commands answer different questions, and the distinction matters:

- **A catalog refresh** (`marketplace update`) re-reads which plugins exist. A
  newly published plugin shows up in **Discover** as soon as you run it, with no
  `version` field involved — until then, `/plugin install` will tell you it
  doesn't exist.
- **A plugin update** (`/plugin update`) pulls new content for plugins you already
  installed, and only lands when we bump that plugin's `version`. A refresh that
  reports no change usually means nothing was released.

## Removing plugins

```shell
/plugin disable tsh-product-design@tsh-agentic-collections     # keep, stop loading
/plugin uninstall tsh-product-design@tsh-agentic-collections   # remove one plugin
/plugin marketplace remove tsh-agentic-collections             # remove everything
```

⚠️ Removing the marketplace also uninstalls every plugin you installed from it.

## The plugins

### Core — *the ground under both*

Everyone, at **User** scope.

| Plugin | Covers | Install |
| :-- | :-- | :-- |
| [`tsh-core`](plugins/tsh-core) | What holds regardless of role and stack — Git worktree lifecycle, the house standard for writing technical documents, authoring Claude Code extensions, the project-context files Claude Code loads, the decision-record format, a one-command project setup, and the bundled Atlassian and Figma MCP servers | `/plugin install tsh-core@tsh-agentic-collections` |

One plugin, not a family. Anything that would change if you switched job belongs in
a discipline plugin; anything that would change if the repo switched language
belongs in a stack plugin. There is no cap on what lands here, but the bar is the
highest in the repo and every addition states what it costs — everyone installs
this one, so every skill in it spends every teammate's context.

### Disciplines — *how we work*

Install the one that matches your job, at **User** scope.

| Plugin | Covers | Install |
| :-- | :-- | :-- |
| [`tsh-product-engineering`](plugins/tsh-product-engineering) | Feature implementation, code review, refactoring, debugging, TDD workflows | `/plugin install tsh-product-engineering@tsh-agentic-collections` |
| [`tsh-product-testing`](plugins/tsh-product-testing) | E2E testing, accessibility testing, exploratory/manual QA, test-plan authoring | `/plugin install tsh-product-testing@tsh-agentic-collections` |
| [`tsh-product-management`](plugins/tsh-product-management) | Workshop materials to a Jira-ready backlog: intent brief, epics and user stories, an eleven-pass quality review, and an outcome-based delivery roadmap — five review gates, with the Jira push enforced by a hook | `/plugin install tsh-product-management@tsh-agentic-collections` |
| [`tsh-product-design`](plugins/tsh-product-design) | UI/UX design work, design systems, design review, Figma-driven flows | `/plugin install tsh-product-design@tsh-agentic-collections` |
| [`tsh-platform-engineering`](plugins/tsh-platform-engineering) | Infrastructure, CI/CD, IaC, containers, observability, deployment | `/plugin install tsh-platform-engineering@tsh-agentic-collections` |

### Stacks — *what we work with*

Install what the project is built on, at **Project** scope.

| Plugin | Covers | Install |
| :-- | :-- | :-- |
| [`tsh-stack-frontend`](plugins/tsh-stack-frontend) | TypeScript for the browser: version policy, the `tsconfig` baseline for a bundler-resolved app, the React + Vite split-config layout, and getting a real type-check into CI | `/plugin install tsh-stack-frontend@tsh-agentic-collections` |
| [`tsh-stack-nodejs`](plugins/tsh-stack-nodejs) | TypeScript for Node: version policy, the `tsconfig` baseline for a Node runtime, decorator metadata and class fields; NestJS 11 REST APIs | `/plugin install tsh-stack-nodejs@tsh-agentic-collections` |
| [`tsh-stack-serverless`](plugins/tsh-stack-serverless) | AWS Lambda on OSLS: which libraries we use and which we avoid, how a serverless project is structured, least-privilege IAM, reserved concurrency, secrets at runtime, Step Functions task rules, and checks that execute the packaged artifact | `/plugin install tsh-stack-serverless@tsh-agentic-collections` |
| [`tsh-stack-python`](plugins/tsh-stack-python) | Modern Python 3.12+: implementation and review practices, and Pydantic v2 / dataclass / SQLModel / SQLAlchemy 2.0 data modelling | `/plugin install tsh-stack-python@tsh-agentic-collections` |
| [`tsh-stack-aws`](plugins/tsh-stack-aws) | AWS: Terraform patterns for VPC, EKS, RDS and S3, Well-Architected defaults, and an evidence-based cost and tagging audit of a live account | `/plugin install tsh-stack-aws@tsh-agentic-collections` |
| [`tsh-stack-gcp`](plugins/tsh-stack-gcp) | GCP: Terraform patterns for VPC, GKE, Cloud SQL, Cloud Storage and Cloud Run, Workload Identity and CMEK defaults, and a cost and labelling audit of a live project | `/plugin install tsh-stack-gcp@tsh-agentic-collections` |
| [`tsh-stack-azure`](plugins/tsh-stack-azure) | Azure: Terraform patterns for VNet, AKS, Flexible Server, Blob Storage, Application Gateway and Key Vault, Managed Identity defaults, and a cost and tagging audit via Resource Graph | `/plugin install tsh-stack-azure@tsh-agentic-collections` |

A stack here is a **runtime target** or a **cloud provider**, not a language — a
repository has one cloud and one or more runtime targets. The frontend, Node and serverless plugins all
carry TypeScript guidance, because a browser app, a Node service and a Lambda bundle
genuinely need different compiler configuration — and because most projects have a
frontend whatever their backend is written in. Install the ones the repo is built on.

Every stack gets its own plugin, named `tsh-stack-<stack-name>` — PHP, Java, Go
and the rest are expected members of this family. Each appears here once it has
real content to ship, rather than as an empty placeholder.

> **Coming from `tsh-stack-typescript`?** It has been split into the two plugins
> above. There is no automatic migration, so run:
>
> ```shell
> /plugin uninstall tsh-stack-typescript@tsh-agentic-collections
> /plugin marketplace update tsh-agentic-collections
> /plugin install tsh-stack-frontend@tsh-agentic-collections
> /plugin install tsh-stack-nodejs@tsh-agentic-collections
> ```
>
> `implementing-nestjs-api` moved to `tsh-stack-nodejs` unchanged. The old
> `typescript-conventions` skill is gone: its compiler and version material now
> lives in each plugin's `configuring-typescript-for-<target>` skill, and its type
> modelling material was dropped rather than duplicated — it will return as its own
> skill.

## Troubleshooting

**`/plugin` isn't recognized.** Your Claude Code is too old. Update it, restart your
terminal, and try again.

**A plugin shows as `✘ disabled` in `claude plugin list`.** Check where you ran it.
`plugin list` reports every plugin you've installed, anywhere, but `Status` reflects
the **current directory** — a `project` or `local` scoped plugin is correctly disabled
outside its project. Run it again from that project's root and it should read
`✔ enabled`.

**A plugin listed in this README isn't in the Discover tab.** Your cached copy of the
catalog predates it. `/plugin` never re-fetches on its own and auto-update is off by
default, so refresh it — see [Staying current](#staying-current). `/plugin update`
won't help: that updates plugins you already have, not the list of what exists.

**Skills or agents don't appear after installing.** Delete the marketplace's cached
clone, restart Claude Code, then re-add (Step 1) and reinstall (Step 2):

```shell
rm -rf ~/.claude/plugins/marketplaces/tsh-agentic-collections
```

`~/.claude/plugins/known_marketplaces.json` is the index that tracks the clone and
where it lives. (Older docs point at `~/.claude/plugins/cache` — that path no longer
exists, so removing it does nothing.)

**Anything else.** Run `/plugin` and open the **Errors** tab — load failures are
reported there with the reason.

## Contributing

Read [`CLAUDE.md`](CLAUDE.md) for conventions, then copy
[`templates/agent.md`](templates/agent.md) or
[`templates/SKILL.md`](templates/SKILL.md) into the right plugin.

Test against the working tree without installing anything:

```shell
claude --plugin-dir ./plugins/tsh-product-testing
claude plugin validate ./plugins/tsh-product-testing
python3 scripts/lint-descriptions.py      # flags skills whose descriptions read alike
```

If you changed a skill or agent description, also run the routing evals. They spend
API budget on your account, about USD 0.12 per case. How to run both checks and read
their output, and when CI runs them: [`evals/README.md`](evals/README.md).

## License

MIT — see [LICENSE](LICENSE).
