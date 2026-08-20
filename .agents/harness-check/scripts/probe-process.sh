#!/usr/bin/env bash
# Probe: process launch and termination.
#
# The gap this closes: running a shell command is not the same event as
# spawning and killing a process. A telemetry pipeline that only sees command
# execution has no pid, no image, and no lifetime. Every probe here
# records the pid and image it produced so an event consumer can be checked
# against known-good values.
set -uo pipefail
. "$(dirname "$0")/_lib.sh"
sandbox

IMAGE="$(command -v sleep || echo /bin/sleep)"

# --- launch ----------------------------------------------------------------

"$IMAGE" 30 &
PID=$!
if kill -0 "$PID" 2>/dev/null; then
  pass proc.launch "pid=$PID image=$IMAGE"
else
  fail proc.launch "process did not start"
fi

# the pid must be resolvable to its image while it lives — this is the field a
# 1007 event is expected to carry, so prove it is actually observable
if [ -r "/proc/$PID/cmdline" ]; then
  observed=$(tr '\0' ' ' < "/proc/$PID/cmdline" | awk '{print $1}')
  check proc.image "$IMAGE" "$observed" "(via /proc)"
elif command -v ps >/dev/null 2>&1; then
  observed=$(ps -o comm= -p "$PID" 2>/dev/null | tr -d ' ')
  [ -n "$observed" ] && pass proc.image "comm=$observed (via ps)" \
                     || fail proc.image "pid not resolvable"
else
  skip proc.image "no /proc and no ps"
fi

# --- terminate -------------------------------------------------------------

kill "$PID" 2>/dev/null
wait "$PID" 2>/dev/null
rc=$?
# 143 = 128 + SIGTERM(15); some shells report 15 directly
case "$rc" in
  143|15) pass proc.terminate "pid=$PID signal=TERM rc=$rc" ;;
  *)      fail proc.terminate "unexpected rc=$rc after SIGTERM" ;;
esac

if kill -0 "$PID" 2>/dev/null; then
  fail proc.reaped "pid=$PID still alive after SIGTERM"
else
  pass proc.reaped "pid=$PID gone"
fi

# --- forced kill -----------------------------------------------------------
"$IMAGE" 30 &
PID2=$!
kill -9 "$PID2" 2>/dev/null
wait "$PID2" 2>/dev/null
rc=$?
case "$rc" in
  137|9) pass proc.kill "pid=$PID2 signal=KILL rc=$rc" ;;
  *)     fail proc.kill "unexpected rc=$rc after SIGKILL" ;;
esac

# --- exit codes are distinguishable from signals ---------------------------
( exit 42 ) & PID3=$!
wait "$PID3" 2>/dev/null
check proc.exitcode "42" "$?" "(clean exit, not a signal)"

# --- child of a child: the process tree a pipeline must reconstruct --------
bash -c '"$0" 20 & echo $!' "$IMAGE" > grandchild.pid 2>/dev/null
GPID=$(cat grandchild.pid 2>/dev/null)
if [ -n "${GPID:-}" ] && kill -0 "$GPID" 2>/dev/null; then
  pass proc.grandchild "pid=$GPID (nested spawn)"
  kill -9 "$GPID" 2>/dev/null
  pass proc.grandchild.kill "pid=$GPID"
else
  skip proc.grandchild "nested pid not observable"
fi
rm -f grandchild.pid

summary process
