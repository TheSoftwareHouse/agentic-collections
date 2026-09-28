# Local development

Use this reference when setting up or fixing how a service runs on a
developer's machine: the offline emulator, the local stage, the environment
template, and a local database.

## Table of Contents

- [Install-time settings](#install-time-settings)
- [The emulator is a dependency and a plugin — both](#the-emulator-is-a-dependency-and-a-plugin-both)
- [The local stage](#the-local-stage)
- [.env.dist is the contract, .env is yours](#envdist-is-the-contract-env-is-yours)
- [A local database, when a database was chosen](#a-local-database-when-a-database-was-chosen)
- [A database browser, behind a profile](#a-database-browser-behind-a-profile)
- [One gotcha that costs an afternoon](#one-gotcha-that-costs-an-afternoon)

## Install-time settings

Two lines in `.npmrc`, committed with the service:

```ini
# engines in package.json names the Lambda runtime's Node major. Without this,
# npm only warns on a mismatch: a whole session can run - and pass - on another
# major, and the difference surfaces only in a deployed function.
engine-strict=true
```

That is the install-time half of the rule that `target`, `lib`, `@types/node`
and the declared runtime all name the same Node major — a warning nobody reads
becomes a refusal to install.

Ship `.nvmrc` with the same major next to it, so `nvm use` — or any version
manager that reads it — puts a developer on the right Node before `npm install`
gets the chance to refuse.

**npm 12 blocks packages' install scripts by default** unless they are listed
under `allowScripts`, and prints one warning per blocked package. Do not
approve the list wholesale. esbuild keeps its platform binary in
`optionalDependencies` (`@esbuild/<platform>`) and its blocked `install.js` is
only a fallback, so bundling works with the script blocked — `npx esbuild
--version` is the check. The framework's own post-install scripts are telemetry
and notices; nothing in a deploy depends on them. Approve a script only when
something demonstrably fails without it, one package at a time, and commit the
resulting `allowScripts` entry so the decision is reviewed rather than repeated
on every machine.

## The emulator is a dependency and a plugin — both

`serverless-offline` emulates API Gateway and Lambda locally. It has to be
**installed** in `devDependencies` **and registered** in the service
configuration's `plugins` list; either half alone produces a `serverless
offline` command that does not exist, discovered on the first `npm run dev`.
Pin a major that knows the declared runtime — `nodejs22.x` needs 13.9 or later
on the Serverless Framework v3 line and 14.4 or later on the OSLS v4 line.

Run it against a stage that never deploys:

```shell
serverless offline start --stage local --httpPort 1337 --reloadHandler
```

## The local stage

Keep one stage name — `local` — that exists only for emulation, and derive two
things from it in code:

- **The reserved-concurrency requirement is off.** An emulator has no
  concurrency control to set, and requiring the value would break a fresh clone
  before it ever reaches AWS. Scope the exemption to exactly this stage name so
  it cannot silently widen to a stage that deploys — see
  [`concurrency-and-vpc.md`](./concurrency-and-vpc.md).
- **The database credential comes from a plain local variable**, not a secrets
  store. The handler's contract — receive an identifier, resolve at runtime —
  is unchanged; only the resolver reads `DATABASE_URL` when the stage is
  `local` and the secrets store otherwise.

## `.env.dist` is the contract, `.env` is yours

Commit `.env.dist` with **every** variable `config/` and the handlers read, each
with a safe placeholder and a one-line comment. `.env` is gitignored and never
shown, quoted or logged — when a value is missing, report the variable's
*name*. The test suite never loads `.env` at all: everything a test needs is set
in the test setup, so a run cannot pass locally on an untracked file and fail
in CI.

## A local database, when a database was chosen

Ship a `docker-compose.yaml` with one PostgreSQL service and a `db-up` script
that starts it and waits until it accepts connections. Migrations and seeds run
against it through the same code path production uses, with the local stage
selected. Nothing in the compose file is a real credential.

## A database browser, behind a profile

Ship a web UI for the local database — Adminer is one image, no configuration —
but put it behind a Compose **profile** so the everyday `db:up` starts the
database alone. A developer who wants the panel opts in; nobody else pays for a
container they never open.

```yaml
services:
  db:
    # ... the database service, on a named network
    networks: [app]

  adminer:
    image: adminer
    profiles: [tools]          # not started by `docker compose up -d db`
    ports: ["8080:8080"]
    networks: [app]

networks:
  app:
```

```shell
docker compose --profile tools up -d adminer   # http://localhost:8080
```

**The one thing that trips everyone up:** in the panel, the server is the
Compose **service name** (`db`), not `localhost`. Inside the Adminer container
`localhost` is Adminer itself, so the connection fails with something unhelpful
about refusing connections. Put that sentence in the README next to the command
— it is the single question a new developer asks about this panel.

Both services must sit on the same named network for the service name to
resolve. Credentials in the Compose file stay local-only defaults matching
`.env.dist`, never a real one.

## One gotcha that costs an afternoon

With `serverless-webpack`, `package` and `offline` write to the **same** bundler
output directory. Packaging while an offline server is running overwrites the
bundles underneath it, and the server keeps answering `502` on every route with
nothing in its log. Check for a running offline process before packaging and
stop it, rather than debugging the 502. Verify whether the bundler plugin in
use shares its output directory the same way before assuming it does not.

| Severity | Rule |
| --- | --- |
| MUST | Install `serverless-offline` **and** register it in `plugins`; a missing half is a broken `npm run dev`, not a warning. |
| MUST | Keep exactly one non-deploying stage name, and scope every local exemption to it by name, in code. |
| MUST | Commit `.env.dist` with every variable the service reads; never commit `.env`, and never print its values. |
| MUST | Put any optional local tool — a database browser, a fake AWS — behind a Compose profile, so the default `db:up` starts only what every workflow needs. |
| NEVER | Load `.env` in the test suite — a test that depends on an untracked file passes locally and fails in CI. |

## Sources

Verified 2026-09-18:

- [serverless-offline — Add support for Node.js v22 runtime (#1839)](https://github.com/dherault/serverless-offline/issues/1839)
- [serverless-offline — CHANGELOG](https://github.com/dherault/serverless-offline/blob/master/CHANGELOG.md) — 13.9.0 and 14.4.0 add `nodejs22.x`

The minimum versions above are the ones that first knew `nodejs22.x`; a newer runtime
needs a newer minimum. Check the changelog before pinning.
