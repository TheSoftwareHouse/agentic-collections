#!/usr/bin/env bash
# Run the behavioural eval suites in plugins/*/evals/ — locally only, never in CI.
#
# They build a scratch repository with each case's scaffold script and let Claude
# write files and run commands in it, so they need --scaffold and --allow-tools,
# which the pull-request workflow must never pass (.claude/rules/plugin-evals.md,
# "Security"). Every run bills the signed-in account; the cap below bounds it.
#
#   scripts/run-behaviour-evals.sh                     every plugin that has a suite
#   scripts/run-behaviour-evals.sh tsh-product-testing one plugin
#   RUNS=3 MAX_COST_USD=10 scripts/run-behaviour-evals.sh
set -euo pipefail
cd "$(dirname "$0")/.."

RUNS="${RUNS:-1}"
MAX_COST_USD="${MAX_COST_USD:-5}"
MODEL="${MODEL:-claude-sonnet-5-5}"

# The project-context scripts read a per-person registry and ask the claude CLI for
# its marketplaces. Point both away from this machine's real state, so a case sees
# only what its scaffold built (the same isolation tests/project-context uses).
export TSH_CONTEXT_HOME="${TSH_CONTEXT_HOME:-/nonexistent/tsh-context-home}"
export TSH_CONTEXT_CLAUDE=""

if [ $# -gt 0 ]; then plugins=("$@"); else
  plugins=(); for d in plugins/*/evals; do [ -d "$d" ] && plugins+=("$(basename "$(dirname "$d")")"); done
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
