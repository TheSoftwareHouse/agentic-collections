# Packaging-time template checks

Use this reference when adding, reviewing or debugging a check that runs against the packaged CloudFormation template.

## Table of Contents

- [No wildcard IAM, anywhere in the template](#no-wildcard-iam-anywhere-in-the-template)
- [Every deployed function declares its own concurrency limit](#every-deployed-function-declares-its-own-concurrency-limit)
- [No dangling logical-id reference](#no-dangling-logical-id-reference)
- [Configuration that is present but malformed](#configuration-that-is-present-but-malformed)
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

## Keep the check separate from the source

Write these as scripts (or an equivalent build step) that take the packaged
template's path as input and assert against its actual JSON — not as
assertions embedded in the service configuration itself. That keeps the
check honest: it is asserting over the artifact that will be deployed,
including everything the framework's own plugins injected, rather than over
the hand-written configuration that produced only part of it.
