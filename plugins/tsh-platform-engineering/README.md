# TSH Platform Engineering

Infrastructure, CI/CD, infrastructure as code, containers, observability and deployment.

## Install

```shell
/plugin marketplace add TheSoftwareHouse/agentic-collections
/plugin install tsh-platform-engineering@tsh-agentic-collections
```

## What's in it

Nothing yet — this is a scaffold. `agents/` and `skills/` are empty on purpose.

## Contributing

Add an agent as `agents/<agent-name>.md`, a skill as `skills/<skill-name>/SKILL.md`.
Start from [`templates/agent.md`](../../templates/agent.md) or
[`templates/SKILL.md`](../../templates/SKILL.md), and read
[`CLAUDE.md`](../../CLAUDE.md) for the conventions and the local test loop.

Once installed, components from this plugin are invoked as
`@tsh-platform-engineering:<agent>` and `/tsh-platform-engineering:<skill>`.
