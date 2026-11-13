#!/usr/bin/env bash
# A project folder holding the Acme knowledge base, scaffolded by the plugin's own
# scaffold.py, committed, and pushed to a local bare remote so the write flow has a
# default branch to propose from. No code repository: the locator finds the
# knowledge base beside the session's folder.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPTS="$HERE/../../skills/initializing-project-context/scripts"
export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1 GIT_TERMINAL_PROMPT=0
export GIT_AUTHOR_NAME=Fixture GIT_AUTHOR_EMAIL=fixture@example.com
export GIT_COMMITTER_NAME=Fixture GIT_COMMITTER_EMAIL=fixture@example.com
python3 "$SCRIPTS/scaffold.py" --name "Acme" --slug acme \
  --owner-name "Ola Nowak" --owner-email ola@example.com \
  --catalog-dir "$PWD" --date 2026-11-01 >/dev/null
git -C acme-context init -q -b main
git -C acme-context add -A
git -C acme-context commit -q -m "Initial project context"
git -C acme-context remote add origin "$PWD/acme-context-remote-that-does-not-exist.git"
