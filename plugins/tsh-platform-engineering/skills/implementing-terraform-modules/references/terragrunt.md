# Terraform or Terragrunt

Terragrunt exists to remove repetition across many similar stacks. Below that
threshold it adds a layer to learn and debug for no benefit, so the decision is about
how many near-identical configurations the project actually has.

## Use plain Terraform when

- Single environment, single region.
- Two or three environments in the same region — workspaces or a directory layout per
  environment is enough.
- An existing project that does not already use Terragrunt. **Do not migrate
  mid-project as a side effect of another change** — that is its own decision, with
  its own plan and its own review.

## Use Terragrunt when

- Four or more environments, or multi-region.
- A monorepo of many independent stacks that need `run-all` and dependency ordering.
- Strict environment parity is a requirement, enforced through inheritance rather than
  discipline.
- Multi-account AWS, landing-zone style.
- Greenfield with known growth ahead.

## Terragrunt layout

```text
infrastructure/
├── terragrunt.hcl              # root: remote_state, generated provider blocks
├── _envcommon/                 # shared module references
│   ├── vpc.hcl
│   ├── eks.hcl
│   └── rds.hcl
├── dev/
│   ├── env.hcl                 # environment-level variables
│   ├── vpc/terragrunt.hcl
│   └── eks/terragrunt.hcl
├── staging/
│   └── ...
└── prod/
    └── ...
```

What each layer owns:

- **Root `terragrunt.hcl`** — remote state configuration and generated provider
  blocks. Defined once; every stack inherits it. This is the main repetition
  Terragrunt removes.
- **`_envcommon/`** — one file per component, holding the module source, its version,
  and the inputs common to all environments.
- **`env.hcl`** — what genuinely differs per environment: account, region, sizes,
  scaling bounds.
- **`<env>/<component>/terragrunt.hcl`** — thin: include the root, include the
  `_envcommon` file, override the few inputs specific to this environment.

A stack file growing past a handful of overrides means the difference belongs in
`env.hcl`, or the component needs a variable it does not yet expose.

## Cautions

- **`run-all apply` applies everything it resolves.** Use it deliberately, and never
  as the mechanism behind an automated production deploy without an approval gate.
- **Dependency blocks read outputs from other stacks' state.** A stack that has never
  been applied has no outputs, so a first-time `run-all plan` on a fresh environment
  fails in ways that look like configuration errors. Apply foundational stacks first.
- **Version-pin the module sources** in `_envcommon`. A floating `ref` means two
  environments can silently run different module versions.
