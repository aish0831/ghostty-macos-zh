#!/usr/bin/env bash
set -euo pipefail

project_root=$(git rev-parse --show-toplevel)
cd "$project_root"

failures=0

report_matches() {
  local label=$1
  local matches=$2
  if [[ -n "$matches" ]]; then
    echo "privacy audit failed: $label" >&2
    echo "$matches" >&2
    failures=1
  fi
}

attribution_matches=$(git log --all --format='%H%n%B' | grep -Ein '^(Co-authored-by|Generated-by|Assisted-by):' || true)
report_matches "automated or secondary attribution trailer found" "$attribution_matches"

path_matches=$(git grep -nIE '(/Users/[^/[:space:]]+|/home/[^/[:space:]]+|[A-Za-z]:\\Users\\[^\\[:space:]]+)' -- ':!scripts/privacy-audit.sh' || true)
report_matches "local home-directory path found" "$path_matches"

secret_matches=$(git grep -nIE '(gh[opusr]_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]{20,}|AKIA[0-9A-Z]{16}|BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY)' || true)
report_matches "credential-like value found" "$secret_matches"

email_matches=$(git grep -nIE '[A-Za-z0-9._%+-]+@(corp|internal|local)(\.[A-Za-z0-9.-]+)+' || true)
report_matches "internal-looking email domain found" "$email_matches"

if [[ $failures -ne 0 ]]; then
  exit 1
fi

echo "privacy audit passed"
