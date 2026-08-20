#!/usr/bin/env bash
# Summarize the effective (latest) result for every probe in one run log.
set -euo pipefail
. "$(dirname "$0")/_lib.sh"

[ -s "$HARNESS_CHECK_LOG" ] || {
  echo "no correlation log at $HARNESS_CHECK_LOG" >&2
  exit 1
}

awk -F '\t' '
  $2 ~ /^(PASS|FAIL|SKIP)$/ {
    if ($3 in result && result[$3] != $2)
      transitions[$3] = transitions[$3] result[$3] "->" $2 ";"
    result[$3] = $2
    detail[$3] = $4
    order[$3] = ++sequence
  }
  END {
    for (id in result) {
      count[result[id]]++
      ids[order[id]] = id
    }
    printf "effective: %d PASS / %d SKIP / %d FAIL\n", count["PASS"]+0, count["SKIP"]+0, count["FAIL"]+0
    for (i = 1; i <= sequence; i++) {
      id = ids[i]
      if (id == "") continue
      printf "%-5s %-38s %s", result[id], id, detail[id]
      if (transitions[id] != "") printf " [superseded: %s]", transitions[id]
      printf "\n"
    }
  }
' "$HARNESS_CHECK_LOG"
