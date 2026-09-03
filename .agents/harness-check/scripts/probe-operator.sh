#!/usr/bin/env bash
# Correlation markers for user-operated harness activities.
set -uo pipefail
HERE="$(dirname "$0")"

STEPS=$(cat <<'TSV'
manual.approval-deny	approval.deny	Decline a harmless requested action
manual.approval-allow	approval.allow	Approve a harmless requested action
automatic.approval-allow	approval.auto-allow	Automatic reviewer approved a requested action
automatic.approval-deny	approval.auto-deny	Automatic reviewer denied a requested action
manual.claude.permission-mode	permission.change	Switch Claude Code to manual permission mode
manual.claude.permission-restore	permission.change	Restore the original Claude Code permission mode
manual.codex.config-write	configuration.change	Make or restore a reversible UI-only Codex configuration change
TSV
)

lookup() { awk -F '\t' -v id="$1" '$1 == id {print; found=1} END {exit !found}' <<< "$STEPS"; }

list_steps() {
  printf '%-28s %-22s %s\n' STEP ACTIVITY ACTION
  while IFS=$'\t' read -r id activity action; do
    printf '%-28s %-22s %s\n' "$id" "$activity" "$action"
  done <<< "$STEPS"
}

begin_step() {
  local id="${1:-}"
  lookup "$id" >/dev/null || { echo "unknown step: $id" >&2; exit 1; }
  _emit BEGIN "$id" "waiting for operator"
}

mark_step() {
  local id="${1:-}" result="${2:-}" detail="${3:-}"
  lookup "$id" >/dev/null || { echo "unknown step: $id" >&2; exit 1; }
  case "$result" in
    PASS) pass "$id" "$detail" ;;
    FAIL) fail "$id" "$detail" ;;
    SKIP) skip "$id" "$detail" ;;
    *) echo "result must be PASS, FAIL, or SKIP" >&2; exit 2 ;;
  esac
}

show_window() {
  local id="${1:-}" from to
  [ -s "$HARNESS_CHECK_LOG" ] || { echo "no log at $HARNESS_CHECK_LOG" >&2; exit 1; }
  from=$(awk -F '\t' -v id="$id" '$2 == "BEGIN" && $3 == id {print $1}' "$HARNESS_CHECK_LOG" | tail -1)
  to=$(awk -F '\t' -v id="$id" '$2 != "BEGIN" && $3 == id {print $1}' "$HARNESS_CHECK_LOG" | tail -1)
  [ -n "$to" ] || { echo "no completed record for $id" >&2; exit 1; }
  printf '%s\t%s\t%s\n' "$id" "${from:-(no BEGIN stamped)}" "$to"
}

prepare_sequence() {
  [ "$#" -gt 0 ] || { echo "usage: probe-operator.sh prepare <id>..." >&2; exit 2; }
  local id ids=""
  for id in "$@"; do
    lookup "$id" >/dev/null || { echo "unknown step: $id" >&2; exit 1; }
    ids="${ids}${ids:+,}$id"
  done
  _emit BEGIN manual.sequence "prepared:$ids"
}

batch_mark() {
  [ "$#" -gt 0 ] || {
    echo "usage: probe-operator.sh batch-mark <id>=PASS|FAIL|SKIP ..." >&2
    exit 2
  }
  local item id result
  # Validate the entire batch before writing any result.
  for item in "$@"; do
    id=${item%=*}
    result=${item##*=}
    [ "$id" != "$item" ] || { echo "invalid result: $item" >&2; exit 2; }
    lookup "$id" >/dev/null || { echo "unknown step: $id" >&2; exit 1; }
    case "$result" in
      PASS|FAIL|SKIP) ;;
      *) echo "result must be PASS, FAIL, or SKIP: $item" >&2; exit 2 ;;
    esac
  done
  for item in "$@"; do
    id=${item%=*}
    result=${item##*=}
    case "$result" in
      PASS) pass "$id" "observed during prepared manual sequence" ;;
      FAIL) fail "$id" "observed during prepared manual sequence" ;;
      SKIP) skip "$id" "unavailable during prepared manual sequence" ;;
    esac
  done
  _emit COMPLETE manual.sequence "manual outcomes stored"
}

# `list` is read-only and must work before a run directory exists — the
# inventory calls it. Every other subcommand writes to the correlation log
# and therefore needs the sandbox from _lib.sh.
case "${1:-list}" in
  list) list_steps; exit 0 ;;
  prepare|batch-mark|begin|mark|window) ;;
  *) echo "usage: probe-operator.sh list|prepare <id>...|batch-mark <id>=RESULT...|begin|mark|window" >&2; exit 2 ;;
esac

. "$HERE/_lib.sh"

case "$1" in
  prepare) shift; prepare_sequence "$@" ;;
  batch-mark) shift; batch_mark "$@" ;;
  begin) shift; begin_step "$@" ;;
  mark) shift; mark_step "$@" ;;
  window) shift; show_window "$@" ;;
esac
