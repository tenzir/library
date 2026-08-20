#!/usr/bin/env bash
# Run every scriptable probe and print an aggregate verdict.
#
#   run-all.sh              all safe scripted probes, including network
#   run-all.sh --no-net     skip outbound network
#   run-all.sh --clean      remove the sandbox and exit
#
# Agent-agnostic: plain bash + python3. Works under any agent, or by hand.
# Point the sandbox somewhere specific by exporting HARNESS_CHECK_DIR first.
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
[ -n "${HARNESS_CHECK_DIR:-}" ] || {
  HARNESS_CHECK_DIR=$(bash "$HERE/new-run.sh" "${HARNESS_CHECK_AGENT:-generic}")
  export HARNESS_CHECK_DIR
}
. "$HERE/_lib.sh"

if [ "${1-}" = "--clean" ]; then
  validate_sandbox_path
  [ -f "$HARNESS_CHECK_DIR/.harness-check-owned" ] || {
    echo "harness-check: refusing to clean unowned directory: $HARNESS_CHECK_DIR" >&2
    exit 2
  }
  rm -rf "$HARNESS_CHECK_DIR"   # includes .lock
  echo "removed $HARNESS_CHECK_DIR"
  exit 0
fi

NET_ARG="--net"
[ "${1-}" = "--no-net" ] && NET_ARG=""

# Hold the lock across every probe, so a second run cannot slip between them.
lock_acquire

echo "sandbox: $HARNESS_CHECK_DIR"
echo "log:     $HARNESS_CHECK_LOG"
echo
rm -f "$HARNESS_CHECK_LOG"

failed=0
for probe in probe-files.sh probe-bash.sh probe-process.sh probe-cli.sh \
             probe-fixtures.sh; do
  echo "== $probe"
  case "$probe" in
    probe-cli.sh)    bash "$HERE/$probe" $NET_ARG ;;
    *)               bash "$HERE/$probe" ;;
  esac
  [ $? -ne 0 ] && failed=$((failed + 1))
  echo
done

if [ "$failed" -eq 0 ]; then
  echo "ALL SCRIPTED ACTIVITIES COMPLETED (skips are not failures)"
else
  echo "$failed PROBE GROUP(S) REPORTED FAILURES"
fi

cat <<'NOTE'

Continue with the native calls in reference/agent-probes.md. Real MCP, skill,
plugin, hook, scheduler, permission, and subagent telemetry must be generated
through the harness itself; this suite never substitutes a mock server or a
lookalike file write. Then follow reference/manual-probes.md one step at a time.
NOTE

exit "$failed"
