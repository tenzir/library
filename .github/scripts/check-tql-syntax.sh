#!/usr/bin/env bash
set -euo pipefail

export TENZIR_BINARY="${TENZIR_BINARY:-uvx tenzir}"

read -r -a tenzir <<< "$TENZIR_BINARY"
if ((${#tenzir[@]} == 0)); then
  printf 'error: TENZIR_BINARY must not be empty\n' >&2
  exit 2
fi

files=()
if (($# > 0)); then
  files=("$@")
else
  while IFS= read -r -d '' file; do
    files+=("$file")
  done < <(git ls-files -z '*.tql')
fi

if ((${#files[@]} == 0)); then
  exit 0
fi

jobs="${TQL_SYNTAX_JOBS:-}"
if [[ -z "$jobs" ]]; then
  if command -v nproc >/dev/null 2>&1; then
    jobs="$(nproc)"
  else
    jobs="$(sysctl -n hw.ncpu 2>/dev/null || printf '4')"
  fi
fi

if [[ ! "$jobs" =~ ^[1-9][0-9]*$ ]]; then
  printf 'error: TQL_SYNTAX_JOBS must be a positive integer\n' >&2
  exit 2
fi

"${tenzir[@]}" --help >/dev/null

printf 'Checking %d TQL files with %s\n' "${#files[@]}" "$TENZIR_BINARY"

printf '%s\0' "${files[@]}" |
  xargs -0 -n 1 -P "$jobs" bash -c '
    set -euo pipefail

    read -r -a tenzir <<< "$TENZIR_BINARY"
    file="$1"

    if [[ "$file" == */tests/inputs/*.tql ]]; then
      if ! TQL_SYNTAX_FILE="$file" "${tenzir[@]}" \
        '\''from_file f"{env("TQL_SYNTAX_FILE")}" { read_tql }'\'' >/dev/null; then
        printf "::error file=%s::invalid TQL data\n" "$file" >&2
        exit 1
      fi
      exit 0
    fi

    if ! "${tenzir[@]}" --dump-ast -f "$file" >/dev/null; then
      printf "::error file=%s::invalid TQL pipeline\n" "$file" >&2
      exit 1
    fi
  ' _
