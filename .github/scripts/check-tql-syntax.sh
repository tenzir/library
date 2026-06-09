#!/usr/bin/env bash
set -euo pipefail

# Validate TQL syntax for tracked files with the prerelease Tenzir CLI.
#
# Example and test pipelines are complete pipelines, so we compile them all the
# way to IR (--dump-ir), which resolves operators, their arguments, and
# references on top of parsing. Operator definitions are parameterized templates
# whose arguments only bind at the call site, so they cannot be compiled
# standalone; we check their syntax with --dump-ast. They are still exercised
# through IR by the test pipelines that call them.
#
# CI checks all tracked files; pre-push uses --changed for files changed since
# the merge base with the upstream branch.

parallelism="$(getconf _NPROCESSORS_ONLN 2>/dev/null || printf '8')"
tenzir=(uvx --prerelease allow tenzir)

# Loading the repository as a package directory lets IR resolve the
# package-defined operators that examples and test pipelines reference.
TENZIR_PACKAGE_DIRS="$(git rev-parse --show-toplevel)"
export TENZIR_PACKAGE_DIRS

# Operator definitions: syntax-only check (templates can't compile standalone).
operator_files=('*/operators/*.tql')
# Examples and test pipelines: full IR compilation. Skip data test inputs; they
# are fixtures, not pipelines.
pipeline_files=('*.tql' ':!:*/tests/inputs/*.tql' ':!:*/operators/*.tql')

base_ref() {
  git rev-parse --verify --quiet '@{upstream}' >/dev/null &&
    git rev-parse --abbrev-ref --symbolic-full-name '@{upstream}' &&
    return
  git rev-parse --verify --quiet origin/HEAD >/dev/null && printf 'origin/HEAD\n'
}

list_files() {
  if [[ "${changed}" != 1 ]]; then
    git ls-files -z "$@"
    return
  fi
  local base ref
  ref="$(base_ref)" || {
    git ls-files -z "$@"
    return
  }
  base="$(git merge-base HEAD "$ref")" || {
    git ls-files -z "$@"
    return
  }
  # Check only local commits being pushed. On main, this means commits ahead of
  # origin/main; remote-only changes are not part of the pre-push check.
  git diff --name-only -z --diff-filter=ACMRT "$base" HEAD -- "$@"
}

# Run the given dump flag over all files matching the trailing pathspecs.
check() {
  local flag="$1"
  shift
  local files=()
  while IFS= read -r -d '' file; do
    files+=("$file")
  done < <(list_files "$@")
  ((${#files[@]} == 0)) && return 0
  printf '%s\0' "${files[@]}" |
    xargs -0 -n 1 -P "$parallelism" "${tenzir[@]}" "$flag" -f >/dev/null
}

changed=0
[[ "${1:-}" == "--changed" ]] && changed=1

rc=0
check --dump-ir "${pipeline_files[@]}" || rc=1
check --dump-ast "${operator_files[@]}" || rc=1
exit "$rc"
