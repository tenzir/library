#!/usr/bin/env bash
# Create one isolated correlation directory for a single harness invocation.
set -euo pipefail

agent="${1:-generic}"
case "$agent" in
  claude|codex|generic) ;;
  *) echo "usage: new-run.sh [claude|codex|generic]" >&2; exit 2 ;;
esac

base="${TMPDIR:-/tmp}/harness-check-$agent"
run_dir=$(mktemp -d "${base}-$(date -u +%Y%m%dT%H%M%SZ)-XXXXXX")
: > "$run_dir/.harness-check-owned"
printf '%s\n' "$run_dir"
