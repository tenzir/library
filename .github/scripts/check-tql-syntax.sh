#!/usr/bin/env bash
set -euo pipefail

jobs="$(getconf _NPROCESSORS_ONLN 2>/dev/null || printf '4')"

# Ignore data test inputs here; the second pass parses them with read_tql.
git ls-files -z '*.tql' ':!:*/tests/inputs/*.tql' |
  xargs -0 -n 1 -P "$jobs" bash -c '
    (($# == 0)) || uvx --prerelease allow tenzir --dump-ast -f "$1" >/dev/null
  ' _

git ls-files -z '*/tests/inputs/*.tql' |
  xargs -0 -n 1 -P "$jobs" bash -c '
    (($# == 0)) || TQL_SYNTAX_FILE="$1" uvx --prerelease allow tenzir \
      '\''from_file f"{env("TQL_SYNTAX_FILE")}" { read_tql }'\'' >/dev/null
  ' _
