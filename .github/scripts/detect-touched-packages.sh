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

# Shared test tooling affects every package.
while IFS= read -r path; do
  case "$path" in
    .github/*)
      printf '.\n'
      exit 0
      ;;
  esac
done <<< "$diff_output"

candidate_lines=$(printf '%s\n' "$diff_output" | awk -F/ 'NF>1 && $1 !~ /^\./ {print $1}' | sort -u)

filtered=()
while IFS= read -r candidate; do
  [[ -z "$candidate" ]] && continue
  if [[ -f "$candidate/package.yaml" ]]; then
    filtered+=("$candidate")
  fi
done <<< "$candidate_lines"

# Tests of a package can load other packages through `package-dirs` in a
# `test.yaml`. A change to such a package also selects the dependent package.
package_dir_entries() {
  awk '
    /^package-dirs:/ { in_list = 1; next }
    in_list && /^[[:space:]]*-[[:space:]]*/ {
      sub(/^[[:space:]]*-[[:space:]]*/, "")
      sub(/[[:space:]]+#.*$/, "")
      gsub(/^["\047]|["\047]$/, "")
      print
      next
    }
    in_list && !/^[[:space:]]*(#.*)?$/ { in_list = 0 }
  ' "$1"
}

# Repeat until no package gets added, since a dependent package can itself be
# loaded by the tests of another one.
root=$(pwd -P)
added=1
while (( ${#filtered[@]} > 0 && added )); do
  added=0
  for manifest in */package.yaml; do
    dependent="${manifest%/package.yaml}"
    [[ -d "$dependent/tests" ]] || continue
    [[ " ${filtered[*]} " == *" $dependent "* ]] && continue
    while IFS= read -r config; do
      config_dir=$(dirname "$config")
      while IFS= read -r entry; do
        [[ -z "$entry" ]] && continue
        resolved=$(realpath -m "$config_dir/$entry")
        [[ "$resolved" == "$root"/* ]] || continue
        if [[ " ${filtered[*]} " == *" ${resolved#"$root"/} "* ]]; then
          filtered+=("$dependent")
          added=1
          continue 3
        fi
      done < <(package_dir_entries "$config")
    done < <(find "$dependent/tests" -name test.yaml -type f | sort)
  done
done

if (( ${#filtered[@]} == 0 )); then
  printf '\n'
else
  printf '%s\n' "${filtered[*]}"
fi
