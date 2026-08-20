#!/usr/bin/env bash
# Append an agent-driven or manual probe result to the shared correlation log.
set -uo pipefail
. "$(dirname "$0")/_lib.sh"

result="${1:-}"
id="${2:-}"
detail="${3:-}"
[ -n "$id" ] || { echo "usage: record.sh PASS|FAIL|SKIP <probe-id> [detail]" >&2; exit 2; }

case "$result" in
  PASS) pass "$id" "$detail" ;;
  FAIL) fail "$id" "$detail" ;;
  SKIP) skip "$id" "$detail" ;;
  *) echo "result must be PASS, FAIL, or SKIP" >&2; exit 2 ;;
esac
