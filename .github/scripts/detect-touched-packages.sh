#!/usr/bin/env bash
set -eo pipefail

base_ref="${1:-}"

if [[ -z "$base_ref" ]]; then
  printf '.\n'
  exit 0
fi

if ! diff_output=$(git diff --name-only "${base_ref}"...HEAD 2>/dev/null); then
  printf '.\n'
  exit 0
fi

candidate_lines=$(printf '%s\n' "$diff_output" | awk -F/ 'NF>1 && $1 !~ /^\./ {print $1}' | sort -u)

filtered=()
while IFS= read -r candidate; do
  [[ -z "$candidate" ]] && continue
  if [[ -f "$candidate/package.yaml" ]]; then
    filtered+=("$candidate")
  fi
done <<< "$candidate_lines"

if (( ${#filtered[@]} == 0 )); then
  printf '\n'
else
  printf '%s\n' "${filtered[*]}"
fi
