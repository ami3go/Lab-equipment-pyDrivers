#!/usr/bin/env bash
#
# Run the same checks CI runs, locally.
#
#   ./scripts/run_ci.sh              # offline checks (no network needed)
#   ./scripts/run_ci.sh --remote     # also resolve every indexed GitHub repo
#
# Exits non-zero on the first failing check, so it can be used as a
# pre-commit hook or a `make ci` target.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

REMOTE=0
for arg in "$@"; do
  case "$arg" in
    --remote) REMOTE=1 ;;
    *) echo "unknown option: $arg" >&2; exit 2 ;;
  esac
done

step() { printf '\n==> %s\n' "$1"; }

step "Index consistency (scripts/check_index.py)"
if [ "$REMOTE" -eq 1 ]; then
  if [ -z "${GITHUB_TOKEN:-}" ] && [ -z "${GH_TOKEN:-}" ]; then
    echo "note: GITHUB_TOKEN/GH_TOKEN is not set; the anonymous GitHub API allows"
    echo "      only 60 requests per hour, which is fewer than this index needs."
    echo "      The remote check will report a rate-limit warning instead of failing."
  fi
  python3 scripts/check_index.py --check-remote
else
  python3 scripts/check_index.py
fi

step "Unit tests for the index checker"
python3 -m unittest discover -s scripts -p 'test_*.py' -v

step "Markdown lint (markdownlint-cli2)"
if command -v npx >/dev/null 2>&1; then
  npx --yes markdownlint-cli2@0.14.0
else
  echo "npx not found -- skipping the markdown lint step locally." >&2
  echo "CI runs it with Node 20; install Node to reproduce that step." >&2
fi

printf '\nAll CI checks passed.\n'
