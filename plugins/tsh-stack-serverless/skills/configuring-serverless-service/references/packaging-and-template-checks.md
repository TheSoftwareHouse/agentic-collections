# Packaging-time template checks

Use this reference when adding, reviewing or debugging a check that runs against the packaged CloudFormation template.

## Table of Contents

- [No wildcard IAM, anywhere in the template](#no-wildcard-iam-anywhere-in-the-template)
- [Every deployed function declares its own concurrency limit](#every-deployed-function-declares-its-own-concurrency-limit)
- [No dangling logical-id reference](#no-dangling-logical-id-reference)
- [Configuration that is present but malformed](#configuration-that-is-present-but-malformed)
- [Execute the packaged artifact](#execute-the-packaged-artifact)
- [The verify gate](#the-verify-gate)
- [Keep the check separate from the source](#keep-the-check-separate-from-the-source)

`package` (or the packaging step of `deploy`) produces the CloudFormation
template that will actually be sent to AWS. That is the last moment where
catching a mistake is cheap: after packaging, the next place most of these
mistakes surface is minutes into a deploy, or on the first real production
request. Run assertions against the **packaged template itself**, not
against the source configuration — the framework and its plugins generate
resources the source never mentions (a stage's default execution role, a
custom resource for a plugin's own setup), and those generated resources are
exactly the ones nobody reads by hand.

Treat these as a build gate: a failing check should fail the build, the same
way a failing test does. What to assert, and why each one is worth the
cost:

## No wildcard IAM, anywhere in the template

Walk every `AWS::IAM::Role` (or equivalent) resource in the packaged
template, not only the roles this service's own configuration wrote. For
every policy statement on every role:

- **No wildcard action.** An action string containing `*` is a defect,
  full stop — the fix is to name the actions instead of pattern-matching
  them.
- **No `Resource: "*"`**, unless every action in that statement is one of
  the named, unscopeable exceptions from
  [`iam-and-secrets.md`](./iam-and-secrets.md#the-wildcard-carve-out). Keep
  that exception list next to the check itself, one action at a time, so
  widening it is a reviewed diff rather than a pattern quietly matching
  something new.
- **No attached managed policy.** A managed policy hides its actual grant
  from anyone reading this service's code.

This check has to run over **every** role the template contains, including
ones this service's configuration never wrote — a plugin that adds its own
custom-resource Lambda gets its own role, generated with whatever default
the plugin author chose, and that default is not guaranteed to meet this
service's bar.

## Every deployed function declares its own concurrency limit

For every `AWS::Lambda::Function` resource that represents a real,
deployed-stage function (exempt only the stage(s) used for local emulation —
see [`concurrency-and-vpc.md`](./concurrency-and-vpc.md)), assert that a
reserved-concurrency value is present. A function silently added without one
should fail packaging, not surface as an account-wide throttling incident
weeks later.

## No dangling logical-id reference

CloudFormation logical ids are **derived** from a resource's name by a fixed,
mechanical rule (typically: strip or replace non-alphanumeric characters,
upper-case the first letter). A hand-written `Ref` or `Fn::GetAtt` to a
resource — a state machine, a log group, a role — can guess that derivation
wrong in a way that:

- Still produces valid JSON/YAML.
- Still passes the framework's own schema validation.
- Still packages without a single warning.
- Fails only once CloudFormation actually tries to resolve the reference
  during the deploy — several minutes in, after other resources have already
  changed.

Walk the packaged template for every `Ref` and `Fn::GetAtt` (excluding AWS
pseudo-parameters like `AWS::Region`) and every `DependsOn`, and assert the
referenced logical id actually exists as a resource or parameter in the same
template. Always derive logical ids programmatically from the same naming
rule the framework uses, rather than typing them by hand, and let this check
be the safety net for the cases that slip through anyway.

## Configuration that is present but malformed

A required value being *missing* (a missing environment variable, a missing
reserved-concurrency number) is the easy failure to catch, because it is
usually enforced at the point the configuration is written. A value that is
*present but malformed* is worse, because it passes packaging, passes the
deploy, and often passes a basic health check too — a health endpoint
typically reads none of the configuration that is actually broken. It then
surfaces on the first real request as a runtime configuration error wrapped
in an opaque 500.

Where a function validates its own environment with a schema at runtime,
run that same schema against the environment the function is actually being
packaged with, as part of packaging. Use a placeholder value for anything
CloudFormation only resolves at deploy time (a `Ref` that becomes a real ARN
string only in AWS) — a schema expecting a non-empty string is satisfied by
a placeholder without it pretending to be a real ARN. This gives one
definition of "valid" that both packaging and the running handler agree on,
instead of two definitions that can quietly drift apart.

## Execute the packaged artifact

Every check above reads the template. None of them proves that the code inside
the zips runs. The compiler and bundler skill's rule — *verify by executing the
packaged artifact* — has this shape, in two assertions that both run after
`package` and before any deploy, and neither of which touches AWS:

- **Every packaged bundle loads.** For each function zip, extract it and import
  the handler entry in a fresh Node process. It must load as a module without
  throwing. This is the only cheap moment to catch what the type-check cannot
  see: a CommonJS dependency inside the ESM bundle, a `.js` entry the runtime
  would read as CommonJS, an external that is not actually available, a
  dynamic `require()` the bundler silently left unresolved.
- **The packaged health handler runs.** Invoke the health handler from the
  packaged bundle — not from source — against the local database, with the
  stage's environment resolved locally the way the local stage does. It must
  answer `ok`. That proves the bundle can reach a database through the driver
  the bundler actually produced, which a source-level test runner never
  exercises.

A failure here is a failure of the artifact, not of the source, and the source
suite will not reproduce it. Report it as such.

## The verify gate

One command is the gate, locally and in CI, and a subset of it is not
"verified". The house shape, in order:

```text
verify        = verify:source && verify:artifact
verify:source = check-node-version && typecheck && lint && test:unit && audit
verify:artifact = package --stage <stage> && check:template && check:artifact
```

`audit` fails on known vulnerabilities in the dependency tree — the frozen tree
of an end-of-life framework is exactly what it exists to catch. `test:unit`
excludes `test/integration/`; `test:integration` runs it against the local
database and belongs in CI with a database service. Keep a `verify:offline`
that skips only `audit` for a machine without registry access, and make it say
so in its output rather than reporting the run as fully verified.

## Keep the check separate from the source

Write these as scripts (or an equivalent build step) that take the packaged
template's path as input and assert against its actual JSON — not as
assertions embedded in the service configuration itself. That keeps the
check honest: it is asserting over the artifact that will be deployed,
including everything the framework's own plugins injected, rather than over
the hand-written configuration that produced only part of it.
