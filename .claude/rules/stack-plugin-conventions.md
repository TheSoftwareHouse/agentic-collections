---
paths:
  - "plugins/tsh-stack-*/**"
---

# Stack plugin conventions

**Every technology stack gets its own plugin, named `tsh-stack-<stack-name>`.** PHP,
Java, Go and further cloud providers are expected members of this family; each is created
when it has real content to ship, not before. An empty plugin in the Discover tab teaches
teammates the catalogue is hollow — and so does a plugin holding a single reference file,
so seed a new member with at least one complete skill.

## Two kinds of member

The family has two shapes, and both answer the same routing question — *would this
guidance change if the project switched this technology?*

| Shape | Members | Owns |
| :-- | :-- | :-- |
| **Runtime target for application code** | `tsh-stack-frontend`, `tsh-stack-nodejs`, `tsh-stack-python` | How the project's own code is written, configured and compiled |
| **Cloud provider** | `tsh-stack-aws`, `tsh-stack-gcp`, `tsh-stack-azure` | That provider's resource patterns, service defaults, and account-level audits |

A cloud is a legitimate member for the same reason a runtime is: a repository has
exactly one, and carrying two providers' service tables in every listing is the cost the
family exists to avoid.

The install model is what makes this work, and it is already in `CLAUDE.md`: a
discipline plugin travels with **you** at user scope, a stack plugin with the
**repository** at project scope. An engineer works across clouds; a repository does not.

## The discipline/cloud seam

A cloud plugin and `tsh-platform-engineering` split one subject, so the boundary has to
be stated or it drifts on the next contribution:

| Cloud plugin | `tsh-platform-engineering` |
| :-- | :-- |
| Resource patterns and service defaults for that provider | Tool mechanics — Terraform module structure, state, Terragrunt, Terratest |
| That provider's service inventory, waste checks, cost report | The cloud-agnostic framework — pricing models, tiering, tagging governance |
| — | Pipelines, Kubernetes, observability, secrets |
| — | **All cross-cloud comparison.** `designing-multi-cloud-architecture` needs every provider's tables in one place and can never be split by cloud |

The test: *does this sentence name a provider's service?* If yes, it belongs to the
cloud plugin. If it names a tool, a workflow, or more than one provider, it belongs to
the discipline plugin.

## Parallel naming is a contract

Skills that do the same job for different technologies must be named to a pattern, so
the third one is predictable rather than invented:

- `auditing-<cloud>-cost` — `auditing-aws-cost`, `auditing-gcp-cost`, `auditing-azure-cost`
- `implementing-<cloud>-terraform` — `implementing-aws-terraform`, `implementing-gcp-terraform`, `implementing-azure-terraform`
- `configuring-typescript-for-<target>` — the runtime-target precedent

A fourth cloud joins by taking the same two names, not by inventing a third shape.

Breaking the pattern is worse than a poor name: a reader who knows one skill can no
longer guess the other, and neither can the model.

## No delegation instructions between plugins

A discipline plugin must not instruct the model to invoke a stack plugin's skill.
**Descriptions carry the routing** — `implementing-nestjs-api` fires because its
description matches, not because `tsh-product-engineering` sends it work, and those two
plugins do not reference each other at all.

The reason is scope: a user-scope discipline plugin pointing at a project-scope stack
plugin dangles on every repository that has not installed one. Where a discipline skill
genuinely needs to mention its specific counterpart, it does so as information with the
generic path still intact — never as a required step.

The corollary is that **a stack skill must stand alone.** It cannot borrow a procedure or
a report format from the discipline plugin, because it cannot link to one. That is why the three
`auditing-<cloud>-cost` skills each carry their own workflow: the shape repeats, but the
data sources (Cost Explorer, BigQuery billing export, Cost Management), service families,
tag dialect and report identifiers diverge, which is the divergence test below being
satisfied rather than dodged.

## A stack is a runtime target, not a language

`tsh-stack-frontend` and `tsh-stack-nodejs` both carry TypeScript guidance, and that
is the design rather than a duplication to clean up. Three reasons:

1. **Most projects have a frontend, whatever the backend is.** A Go or PHP team
   writing React must be able to install the frontend guidance without dragging a
   NestJS surface into their skill listing. A language-shaped plugin makes that
   impossible.
2. **The configuration genuinely diverges.** A bundler-resolved browser app
   (`moduleResolution: bundler`, `jsx`, `lib: DOM`, emit owned by Vite) and a Node
   service (`module: nodenext`, `emitDecoratorMetadata`, `outDir`) do not share one
   baseline `tsconfig.json`. There is no language-level core big enough to be worth a
   plugin of its own.
3. **A plugin is one install decision.** The install unit is the plugin, not the
   skill; there is no way to install half of one. Nobody wants "Node guidance but
   explicitly not the TypeScript settings it depends on."

Framework skills live inside their runtime's plugin: `implementing-nestjs-api`
belongs in `tsh-stack-nodejs`, not in a `tsh-stack-nestjs` of its own.

## Split trigger

When a `tsh-stack-*` plugin exceeds roughly **8 skills**, or when more than half its
skills are irrelevant to a typical installer, split it — again along a target
boundary people actually install separately.

For `tsh-stack-nodejs` that would mean a serverless or CLI plugin peeling off if that
guidance grows and stops being relevant to service authors. It does **not** mean one
plugin per framework.

## Deliberate duplication across stack plugins

Two stack plugins needing the same knowledge is expected, and the ban on
cross-plugin links makes sharing impossible — a path into another plugin fails
silently when that plugin is not installed. So the knowledge is **duplicated**, on
purpose: `configuring-typescript-for-frontend` and `configuring-typescript-for-nodejs`
both carry version policy, a strictness ladder, and an upgrade procedure.

Three rules keep that from rotting:

1. **Name the copies differently, and write genuinely different descriptions.** The
   model routes on descriptions; two near-identical ones are a coin flip. Naming the
   target in the skill name is what makes them distinguishable at all.
2. **Let the divergent parts diverge.** Copying a file and never adapting it is how
   the frontend skill ends up recommending `emitDecoratorMetadata`. If a section is
   identical in both copies *and* would stay identical under any future edit, that is
   a signal the content belongs to neither target specifically — reconsider whether
   it needs to ship at all.
3. **When you change one copy, check the other in the same PR.** Say in the commit
   message which copies you touched and which you deliberately left alone.
