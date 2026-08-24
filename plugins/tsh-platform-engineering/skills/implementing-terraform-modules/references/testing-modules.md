# Testing Terraform modules

Use **Terratest** (Go). A module test provisions real infrastructure, so the rules
below are as much about cost and safety as correctness.

## Required structure

Every module ships both:

- **`examples/complete/`** — a root module calling the module under test with
  realistic values, re-exporting its outputs. This is a usage example and the test
  fixture at once, which is what keeps it honest.
- **`tests/module_test.go`** — runs `InitAndApply`, reads outputs, asserts against
  them, and **always** defers `Destroy`.

## Rules

- **Always `t.Parallel()`.** Module tests are slow; serial runs make the suite
  unusable.
- **Always wrap options with `terraform.WithDefaultRetryableErrors`.** Cloud APIs
  return transient errors and a test that fails on one teaches the team to ignore
  failures.
- **Always resolve the fixture path with `runtime.Caller(0)`**, never a hardcoded
  relative path — that breaks the moment the test runs from a different directory.
- **Always defer `Destroy`**, including on assertion failure. A leaked NAT gateway or
  cluster bills until someone notices.
- **Use cost-reducing flags in fixtures** — `single_nat_gateway = true` and the
  equivalents. A test fixture provisioning a production-shaped topology is a recurring
  bill.
- **Provide a plan-only variant** using `InitAndPlanAndShowWithStruct` for fast PR
  validation. It needs no credentials and catches most structural regressions, so it
  can run on every pull request while the apply test runs on a schedule.
- **Use a dedicated test account.** Never run against production, and never against an
  account that also holds shared development infrastructure.
- **Set `-timeout 30m` in CI.** Go's default 10 minutes kills a cluster apply
  mid-flight, leaving orphaned resources that `Destroy` never gets to clean up.

## What to assert

Assert the module's **interface**, not its internals: that outputs exist, have the
expected shape, and that resources are reachable or usable in the way the module
promises. Asserting on generated resource names couples the test to implementation
and breaks on every harmless refactor.

For a network module that means the VPC ID is returned and subnets exist in the
expected availability zones. For a database module, that a connection endpoint is
returned and accepts a connection.
