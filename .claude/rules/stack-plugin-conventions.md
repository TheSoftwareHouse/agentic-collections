---
paths:
  - "plugins/tsh-stack-*/**"
---

# Stack plugin conventions

**Every technology stack gets its own plugin, named `tsh-stack-<stack-name>`.** PHP,
Java, Go and the rest are expected members of this family; each is created when it
has real content to ship, not before. An empty plugin in the Discover tab teaches
teammates the catalogue is hollow.

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
