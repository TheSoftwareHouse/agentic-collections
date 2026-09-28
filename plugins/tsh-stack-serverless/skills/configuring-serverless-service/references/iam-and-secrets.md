# IAM and secrets

Use this reference when writing or reviewing an execution-role statement, or passing a credential to a function.

## Table of Contents

- [Least-privilege execution roles](#least-privilege-execution-roles)
- [The wildcard carve-out](#the-wildcard-carve-out)
- [Secrets: containers vs values](#secrets-containers-vs-values)

Two related but separate concerns: what a function's execution role may do,
and how a function receives a credential without that credential ever
appearing in a template.

## Least-privilege execution roles

**Split roles by capability, not one role per service.** A single shared
execution role means every function can do whatever the most-privileged
function needs — a Lambda that only writes logs and calls one downstream API
should not carry the permissions a database-backed handler needs. Group
functions by what they actually touch (for example: functions with database
access, functions that only orchestrate, a migration runner) and give each
group its own role built from only the statements it needs.

**No managed policies.** A managed policy (`AWSLambdaBasicExecutionRole` and
similar) is permissions nobody reviewing this service's code can see. Write
every statement out explicitly in the role definition, even the boilerplate
CloudWatch Logs statements, so a reviewer sees the whole grant in one place.

**Every statement names concrete actions and a concrete resource.** The
default shape:

```
{
  "Effect": "Allow",
  "Action": ["logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents"],
  "Resource": ["arn:aws:logs:<region>:<account>:log-group:/aws/lambda/<service>-<stage>-*:*"]
}
```

Build the ARN from the service and stage the role is deployed with, never a
literal account id or region typed by hand — that breaks the moment the
service is deployed under a different account or region.

## The wildcard carve-out

The rule is "never widen `Resource` to `*`, never grant a wildcard action" —
but a small, fixed set of AWS actions have **no resource-level ARN syntax at
all**. Treated as a blanket rule with no exception, this is the kind of
constraint a reader tries once, hits an action they cannot scope, and
abandons entirely. State the exception up front instead:

- **X-Ray's write actions** (`xray:PutTraceSegments`,
  `xray:PutTelemetryRecords`, and the sampling-rule read actions) define no
  resource type. Every example AWS publishes for X-Ray uses `Resource: "*"`.
- **CloudWatch Logs' delivery actions** (`logs:CreateLogDelivery`,
  `logs:PutResourcePolicy`, `logs:DescribeResourcePolicies`, and siblings) are
  account-level operations with no resource to scope to. These appear when a
  service enables API Gateway or Step Functions logging.
- **The ENI actions a VPC-attached function needs**
  (`ec2:CreateNetworkInterface`, `ec2:DescribeNetworkInterfaces`,
  `ec2:DeleteNetworkInterface`, and the IP-assignment actions) are likewise
  unscopeable — AWS's own `AWSLambdaVPCAccessExecutionRole` uses `Resource: "*"`
  for exactly these.

Keep this set named explicitly, one action at a time, in whatever check
enforces the rule — not matched by a pattern. Widening it should be a
deliberate, reviewed edit, never something a new statement quietly falls
into. Every action outside this named set that wants `Resource: "*"` is a
defect: scope it, or add it to the set with the reason it cannot be scoped.

## Secrets: containers vs values

**The stack owns the secret's container, never its value.** Declare each
secret the service needs as its own resource (a Secrets Manager secret, or
equivalent), created with a generated placeholder rather than a literal
value. That means:

- Adding a new credential is a reviewed code change, not a request to
  whoever administers the account.
- The real value is entered once, by hand, by whoever owns the account —
  never by a deploy.
- A stack update must never overwrite what was entered by hand. If the
  underlying resource supports "generate once, then leave alone" semantics,
  use them; a plain literal value in the resource definition would both leak
  into the template and clobber the real credential on the next deploy.
- Deleting or replacing the secret resource must not destroy the credential
  — set retention so the container survives a torn-down stack.

**Functions receive an identifier, never a value.** A function's environment
carries `<SOMETHING>_SECRET_ID`, not `<SOMETHING>_SECRET_VALUE`. The handler
resolves the actual value at runtime (in the init phase, so it is fetched
once per warm container, not once per invocation) and never logs it. This is
the concrete mechanism behind the Non-negotiable Rules table's secrets
entry: the reason a value in `environment` is dangerous is that
`environment` becomes part of the template, and the template is what
`lambda:GetFunctionConfiguration` returns.

**The execution role reads exactly one secret.** Scope
`secretsmanager:GetSecretValue` (or the equivalent action for the secret
store in use) to the ARN of the one secret that function needs — built from
the identifier the stack itself generated, never a hand-typed ARN — so a role
can never be granted a secret the service does not know about. The
deployment role that runs `deploy`/`package` should never carry this
permission at all; it packages the container, it never needs the value.

**Adopting an externally managed secret.** When a secret already exists and
is managed elsewhere — a managed database's auto-generated credentials secret
is the common case — let an override variable substitute that existing
identifier and skip creating a new container. The function-facing contract
(receive an identifier, resolve at runtime) stays identical either way.
