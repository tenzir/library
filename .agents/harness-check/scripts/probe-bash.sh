#!/usr/bin/env bash
# Probe: does the Bash tool give us a real, capable shell? Covers arguments,
# environment, stdin/pipes, exit codes, heredocs, quoting, timeouts, and jobs.
set -uo pipefail
. "$(dirname "$0")/_lib.sh"
sandbox

# 1. positional arguments survive the call
argecho() { printf '%s|%s|%s' "$1" "$2" "$3"; }
check bash.args "a|b c|d" "$(argecho a "b c" d)"

# 2. environment variables set for one command only
check bash.env "custom" "$(HARNESS_PROBE_VAR=custom bash -c 'echo "$HARNESS_PROBE_VAR"')"

# 3. exported vars reach child processes
export HARNESS_PROBE_EXPORTED=exported
check bash.env.export "exported" "$(bash -c 'echo "$HARNESS_PROBE_EXPORTED"')"

# 4. stdin and pipes
check bash.pipe "3" "$(printf 'a\nb\nc\n' | wc -l | tr -d ' ')"

# 5. multi-stage pipeline with a filter
check bash.pipeline "b" "$(printf 'a\nb\nc\n' | grep b | head -n1)"

# 6. exit codes propagate
( exit 7 ); check bash.exitcode "7" "$?"

# 7. failing command in a pipeline is visible via pipefail
if ( set -o pipefail; false | true ); then
  fail bash.pipefail "pipefail not honoured"
else
  pass bash.pipefail ""
fi

# 8. heredoc with interpolation and a quoted (literal) heredoc
V=interpolated
check bash.heredoc "$V" "$(cat <<INNER
$V
INNER
)"
check bash.heredoc.quoted '$V' "$(cat <<'INNER'
$V
INNER
)"

# 9. quoting: spaces and globs survive
touch 'file with spaces.txt'
check bash.quoting "1" "$(ls 'file with spaces.txt' | wc -l | tr -d ' ')"
rm -f 'file with spaces.txt'

# 10. command substitution nests
check bash.subst "4" "$(echo "$(echo 2)$(echo 4)" | cut -c2)"

# 11. arithmetic and conditionals
check bash.arith "42" "$(( 6 * 7 ))"

# 12. loops
total=0; for i in 1 2 3; do total=$((total + i)); done
check bash.loop "6" "$total"

# 13. timeout is available and enforced (a hung command must not hang us)
if command -v timeout >/dev/null 2>&1; then
  timeout 1 sleep 5; check bash.timeout "124" "$?"
else
  skip bash.timeout "timeout(1) not installed"
fi

# 14. background jobs within a single invocation
sleep 0.2 & bg_pid=$!
wait "$bg_pid"; check bash.background "0" "$?"

# 15. writing and executing a generated script
cat > generated.sh <<'INNER'
#!/usr/bin/env bash
echo "generated:$1"
INNER
chmod +x generated.sh
check bash.exec.generated "generated:ok" "$(./generated.sh ok)"
rm -f generated.sh

# 16. non-zero exit from a script is observable
cat > failing.sh <<'INNER'
#!/usr/bin/env bash
exit 3
INNER
chmod +x failing.sh
./failing.sh; check bash.exec.failing "3" "$?"
rm -f failing.sh

# 17. stderr is separable from stdout
out=$(bash -c 'echo to-stdout; echo to-stderr >&2' 2>/dev/null)
check bash.stderr "to-stdout" "$out"

# 18. working directory is where we think it is
check bash.cwd "$HARNESS_CHECK_DIR" "$PWD"

summary bash
