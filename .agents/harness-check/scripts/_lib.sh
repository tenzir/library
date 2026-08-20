#!/usr/bin/env bash
# Shared probe harness: sandbox, correlation logging, PASS/FAIL accounting.
#
# Agent-agnostic. Nothing here depends on a particular agent, tool naming
# scheme, or vendor. Requires: bash, coreutils. Optional: python3.

: "${HARNESS_CHECK_DIR:=${TMPDIR:-/tmp}/harness-check-${UID:-user}}"
export HARNESS_CHECK_DIR

INVOCATION_DIR="$PWD"
export INVOCATION_DIR

PASS_COUNT=0
FAIL_COUNT=0
SKIP_COUNT=0

validate_sandbox_path() {
  case "$HARNESS_CHECK_DIR" in
    ""|/|.|..|"${HOME:-/nonexistent}"|"${TMPDIR:-/tmp}")
      echo "harness-check: refusing unsafe HARNESS_CHECK_DIR '$HARNESS_CHECK_DIR'" >&2
      exit 2 ;;
  esac
  case "$HARNESS_CHECK_DIR" in
    /*) ;;
    *) echo "harness-check: HARNESS_CHECK_DIR must be absolute" >&2; exit 2 ;;
  esac
}

ensure_sandbox_owned() {
  validate_sandbox_path
  if [ ! -d "$HARNESS_CHECK_DIR" ]; then
    mkdir -p "$HARNESS_CHECK_DIR" || exit 2
    : > "$HARNESS_CHECK_DIR/.harness-check-owned"
    return
  fi
  if [ ! -f "$HARNESS_CHECK_DIR/.harness-check-owned" ]; then
    if find "$HARNESS_CHECK_DIR" -mindepth 1 -maxdepth 1 -print -quit 2>/dev/null | grep -q .; then
      echo "harness-check: refusing non-owned, non-empty directory: $HARNESS_CHECK_DIR" >&2
      echo "choose a new empty HARNESS_CHECK_DIR" >&2
      exit 2
    fi
    : > "$HARNESS_CHECK_DIR/.harness-check-owned"
  fi
}

# Machine-readable log of every probe, for correlating actions against events
# collected elsewhere. One TSV record per probe: timestamp, result, probe,
# detail. The probe id is the stable activity label.
: "${HARNESS_CHECK_LOG:=$HARNESS_CHECK_DIR/probes.tsv}"

_emit() {
  local result="$1" id="$2" detail="${3-}"
  printf '%-5s %-30s %s\n' "$result" "$id" "$detail"
  mkdir -p "$(dirname "$HARNESS_CHECK_LOG")" 2>/dev/null
  printf '%s\t%s\t%s\t%s\n' \
    "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$result" "$id" "$detail" \
    >> "$HARNESS_CHECK_LOG" 2>/dev/null
}

pass() { PASS_COUNT=$((PASS_COUNT + 1)); _emit PASS "$1" "${2-}"; }
fail() { FAIL_COUNT=$((FAIL_COUNT + 1)); _emit FAIL "$1" "${2-}"; }
skip() { SKIP_COUNT=$((SKIP_COUNT + 1)); _emit SKIP "$1" "${2-}"; }

# check <name> <expected> <actual> [detail]
check() {
  if [ "$2" = "$3" ]; then
    pass "$1" "${4-}"
  else
    fail "$1" "expected '$2', got '$3' ${4-}"
  fi
}

# --- concurrency guard -----------------------------------------------------
# Two runs sharing one sandbox corrupt each other's results silently: probes
# count lines in files the other run is rewriting, and fixtures vanish
# mid-check. Observed 2026-08-18 — two installs on one machine produced
# "expected '4', got '5'" and "fixture not generated", neither of which is a
# real finding. Fail loudly instead.
#
# The lock is re-entrant for one run: whoever acquires it exports
# HARNESS_CHECK_RUN, and child probes inherit that and skip acquisition.
lock_acquire() {
  local lockdir="$HARNESS_CHECK_DIR/.lock" owner
  [ -n "${HARNESS_CHECK_RUN:-}" ] && return 0    # already inside a locked run
  ensure_sandbox_owned
  if ! mkdir "$lockdir" 2>/dev/null; then
    owner=$(cat "$lockdir/pid" 2>/dev/null || echo "")
    if [ -n "$owner" ] && kill -0 "$owner" 2>/dev/null; then
      echo "harness-check: $HARNESS_CHECK_DIR is already in use by pid $owner." >&2
      echo "  Concurrent runs corrupt each other. Either wait, or set" >&2
      echo "  HARNESS_CHECK_DIR to a different path for this run." >&2
      exit 3
    fi
    rm -rf "$lockdir" && mkdir "$lockdir" 2>/dev/null   # stale lock, take it
  fi
  echo $$ > "$lockdir/pid"
  HARNESS_CHECK_RUN=$$
  export HARNESS_CHECK_RUN
  trap 'lock_release' EXIT INT TERM
}

lock_release() {
  [ "${HARNESS_CHECK_RUN:-}" = "$$" ] && rm -rf "$HARNESS_CHECK_DIR/.lock"
  return 0
}

sandbox() {
  ensure_sandbox_owned
  lock_acquire
  cd "$HARNESS_CHECK_DIR" || exit 1
}

summary() {
  printf -- '---- %s: %d passed, %d failed, %d skipped\n' \
    "$1" "$PASS_COUNT" "$FAIL_COUNT" "$SKIP_COUNT"
  [ "$FAIL_COUNT" -eq 0 ]
}
