#!/usr/bin/env bash
# Run the behavioural eval suites in plugins/*/evals/ — locally only, never in CI.
#
# They build a scratch repository with each case's scaffold script and let Claude
# write files and run commands in it, so they need --scaffold and --allow-tools,
# which the pull-request workflow must never pass (.claude/rules/plugin-evals.md,
# "Security"). Every run bills the signed-in account.
#
#   scripts/run-behaviour-evals.sh                         every plugin that has a suite
#   scripts/run-behaviour-evals.sh tsh-product-management  one plugin
#   RUNS=3 MAX_COST_USD=10 scripts/run-behaviour-evals.sh
#
# MAX_COST_USD caps each plugin's run separately, not the total.
#
# Isolation comes from the harness, not from this script: each run gets its own
# temporary HOME and working directory, and a variable exported here does not
# reach the session (only an allowlist and EVAL_* do).
set -euo pipefail
cd "$(dirname "$0")/.."

RUNS="${RUNS:-1}"
MAX_COST_USD="${MAX_COST_USD:-5}"
MODEL="${MODEL:-claude-sonnet-5-5}"

plugins=()
if [ $# -gt 0 ]; then
  plugins=("$@")
else
  for d in plugins/*/evals; do
    if grep -rqs '^tags:.*\bbehaviour\b' "$d"; then plugins+=("$(basename "$(dirname "$d")")"); fi
  done
fi
if [ ${#plugins[@]} -eq 0 ]; then
  echo "No behavioural suites found under plugins/*/evals/ (cases tagged 'behaviour')." >&2
  exit 1
fi

status=0
for p in "${plugins[@]}"; do
  echo "== $p"
  claude plugin eval "plugins/$p" --tag behaviour --runs "$RUNS" \
    --scaffold --allow-tools Bash Write Edit \
    --trust-plugin --no-publish --ablation none \
    --model "$MODEL" --max-cost-usd "$MAX_COST_USD" || status=1
done
exit $status
