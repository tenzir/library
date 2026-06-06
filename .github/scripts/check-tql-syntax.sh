#!/usr/bin/env bash
set -euo pipefail

# Validate TQL pipeline syntax with the prerelease Tenzir parser.
# CI checks all tracked pipelines; pre-push uses --changed for files changed
# since the merge base with the upstream branch.

parallelism="$(getconf _NPROCESSORS_ONLN 2>/dev/null || printf '8')"
tenzir=(uvx --prerelease allow tenzir)

# Skip data test inputs; they are fixtures, not pipelines.
pipeline_files=('*.tql' ':!:*/tests/inputs/*.tql')

list_all_files() {
  git ls-files -z "${pipeline_files[@]}"
}

base_ref() {
  git rev-parse --verify --quiet '@{upstream}' >/dev/null &&
    git rev-parse --abbrev-ref --symbolic-full-name '@{upstream}' &&
    return
  git rev-parse --verify --quiet origin/HEAD >/dev/null && printf 'origin/HEAD\n'
}

list_changed_files() {
  local base ref
  ref="$(base_ref)" || {
    list_all_files
    return
  }
  base="$(git merge-base HEAD "$ref")" || {
    list_all_files
    return
  }
  git diff --name-only -z --diff-filter=ACMRT "$base" HEAD -- \
    "${pipeline_files[@]}"
}

files=()
while IFS= read -r -d '' file; do
  files+=("$file")
done < <([[ "${1:-}" == "--changed" ]] && list_changed_files || list_all_files)

((${#files[@]} == 0)) && exit 0

printf '%s\0' "${files[@]}" |
  xargs -0 -n 1 -P "$parallelism" "${tenzir[@]}" --dump-ast -f >/dev/null
