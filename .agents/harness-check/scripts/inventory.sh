#!/usr/bin/env bash
# Capability inventory — what can actually be probed HERE, right now.
#
# Read-only and fast. This is the opening report: run it before asking the
# operator what to run, so the menu reflects reality instead of assumptions.
#
#   inventory.sh --agent codex|claude
#   inventory.sh --tsv --agent codex
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"

TSV=0
AGENT_OVERRIDE="${HARNESS_CHECK_AGENT:-}"
while [ $# -gt 0 ]; do
  case "$1" in
    --tsv) TSV=1; shift ;;
    --agent) AGENT_OVERRIDE="${2:-}"; shift 2 ;;
    *) echo "usage: inventory.sh [--tsv] [--agent claude|codex]" >&2; exit 2 ;;
  esac
done

rows=()
row() { rows+=("$1	$2	$3	$4"); }   # area, item, status, detail

# --- which agent are we under? --------------------------------------------
AGENT="generic"
[ -n "${CLAUDECODE:-}${CLAUDE_CODE:-}" ] && AGENT="claude"
[ -n "${CODEX_SANDBOX:-}${CODEX_HOME:-}" ] && AGENT="codex"
[ -n "${CURSOR_TRACE_ID:-}" ] && AGENT="cursor"
[ -d "$HOME/.claude" ] && [ "$AGENT" = "generic" ] && AGENT="claude"
[ -n "$AGENT_OVERRIDE" ] && AGENT="$AGENT_OVERRIDE"
row agent detected "$AGENT" "override with HARNESS_CHECK_AGENT"

# --- telemetry export preflight -------------------------------------------
# Report configuration posture without printing endpoints, headers, or other
# potentially sensitive values.
claude_settings="${CLAUDE_CONFIG_DIR:-$HOME/.claude}/settings.json"

claude_setting() {
  # Print one non-secret setting value. Callers must never use this for
  # endpoints, headers, or credentials.
  local key="$1"
  [ -f "$claude_settings" ] && command -v python3 >/dev/null 2>&1 || return 1
  python3 - "$claude_settings" "$key" <<'PY'
import json, sys
try:
    value = json.load(open(sys.argv[1])).get("env", {}).get(sys.argv[2])
except (OSError, ValueError, AttributeError):
    raise SystemExit(1)
if value is None:
    raise SystemExit(1)
print(value)
PY
}

claude_setting_present() {
  # Check a potentially secret setting without returning its value.
  local key="$1"
  [ -f "$claude_settings" ] && command -v python3 >/dev/null 2>&1 || return 1
  python3 - "$claude_settings" "$key" <<'PY'
import json, sys
try:
    value = json.load(open(sys.argv[1])).get("env", {}).get(sys.argv[2])
except (OSError, ValueError, AttributeError):
    raise SystemExit(1)
raise SystemExit(0 if value not in (None, "") else 1)
PY
}

case "$AGENT" in
  claude)
    telemetry_enabled="${CLAUDE_CODE_ENABLE_TELEMETRY:-$(claude_setting CLAUDE_CODE_ENABLE_TELEMETRY 2>/dev/null || true)}"
    enhanced_enabled="${CLAUDE_CODE_ENHANCED_TELEMETRY_BETA:-$(claude_setting CLAUDE_CODE_ENHANCED_TELEMETRY_BETA 2>/dev/null || true)}"
    if [ "$telemetry_enabled" = "1" ]; then
      row telemetry enabled READY "enabled in environment or Claude settings"
    else
      row telemetry enabled BLOCKED "not enabled in environment or Claude settings"
    fi
    if [ -n "${OTEL_EXPORTER_OTLP_ENDPOINT:-}" ] ||
       [ -n "${OTEL_EXPORTER_OTLP_LOGS_ENDPOINT:-}" ] ||
       claude_setting_present OTEL_EXPORTER_OTLP_ENDPOINT ||
       claude_setting_present OTEL_EXPORTER_OTLP_LOGS_ENDPOINT; then
      row telemetry exporter READY "OTLP endpoint configured in environment or Claude settings"
    else
      row telemetry exporter UNKNOWN "no OTLP endpoint found in environment or Claude settings"
    fi
    if [ "$enhanced_enabled" = "1" ]; then
      row telemetry enhanced READY "enabled in environment or Claude settings"
    else
      row telemetry enhanced DEGRADED "not enabled in environment or Claude settings"
    fi
    for signal in LOGS TRACES METRICS; do
      var="OTEL_${signal}_EXPORTER"
      eval "value=\${$var:-}"
      [ -n "$value" ] || value=$(claude_setting "$var" 2>/dev/null || true)
      if [ -n "$value" ]; then
        row telemetry "$(echo "$signal" | tr '[:upper:]' '[:lower:]')" READY "exporter configured"
      else
        row telemetry "$(echo "$signal" | tr '[:upper:]' '[:lower:]')" UNKNOWN "exporter not found"
      fi
    done
    ;;
  codex)
    codex_cfg="${CODEX_HOME:-$HOME/.codex}/config.toml"
    if [ -f "$codex_cfg" ]; then
      codex_otel=$(awk '
        /^\[otel\][[:space:]]*$/ {inside=1; next}
        /^\[/ {inside=0}
        inside {print}
      ' "$codex_cfg")
      if [ -n "$codex_otel" ]; then
        row telemetry enabled READY "[otel] configuration present"
        if grep -Eq 'exporter[[:space:]]*=|otlp-(http|grpc)' <<< "$codex_otel"; then
          row telemetry exporter READY "OTLP exporter configured"
        else
          row telemetry exporter BLOCKED "[otel] has no OTLP exporter"
        fi
      else
        row telemetry enabled BLOCKED "no [otel] section in Codex config"
      fi
    else
      row telemetry enabled BLOCKED "Codex config not found"
    fi
    ;;
  *) row telemetry enabled UNKNOWN "agent-specific telemetry config not detectable" ;;
esac

# --- interpreters ----------------------------------------------------------
for b in bash python3 awk sed grep find; do
  if command -v "$b" >/dev/null 2>&1; then row core "$b" AVAILABLE "$(command -v "$b")"
  else row core "$b" MISSING "scripted probes will not run"; fi
done

# --- optional CLIs ---------------------------------------------------------
for b in git gh jq rg curl uvx node pdftoppm crontab systemctl pgrep; do
  if command -v "$b" >/dev/null 2>&1; then row cli "$b" AVAILABLE "$("$b" --version 2>&1 | head -n1 | cut -c1-40)"
  else row cli "$b" MISSING ""; fi
done

# --- what each scripted probe needs ---------------------------------------
probe_status() { # probe_status <file> <requirement-cmd> <note>
  local f="$1" need="${2:-}" note="${3:-}"
  if [ ! -f "$HERE/$f" ]; then row probe "$f" MISSING "not installed"; return; fi
  if [ -n "$need" ] && ! command -v "$need" >/dev/null 2>&1; then
    row probe "$f" DEGRADED "needs $need — $note"
  else
    row probe "$f" READY "$note"
  fi
}
probe_status probe-files.sh     ""        "file lifecycle"
probe_status probe-bash.sh      ""        "shell execution"
probe_status probe-process.sh   ""        "process lifecycle"
probe_status probe-cli.sh       ""        "CLI and network execution"
probe_status probe-fixtures.sh  python3   "builds material for native-tool probes"

# --- network ---------------------------------------------------------------
if command -v curl >/dev/null 2>&1; then
  code=$(curl -sS -m 8 -o /dev/null -w '%{http_code}' https://example.com 2>/dev/null || echo 000)
  if [ "$code" = "200" ]; then row network shell-egress AVAILABLE "HTTP 200"
  else row network shell-egress BLOCKED "got '$code' — shell network probes will fail"; fi
else
  row network shell-egress UNKNOWN "curl not installed"
fi

# --- isolated MCP fixture --------------------------------------------------
if command -v python3 >/dev/null 2>&1 && [ -f "$HERE/../assets/mcp-server.py" ]; then
  row mcp fixture READY "child harness will use bundled server only"
else
  row mcp fixture BLOCKED "needs python3 and assets/mcp-server.py"
fi

# --- instruction files -----------------------------------------------------
for f in AGENTS.md CLAUDE.md .claude/CLAUDE.md .cursor/rules; do
  [ -e "$f" ] || continue
  if [ -L "$f" ]; then row config "$f" SYMLINK "-> $(readlink "$f") (writes land on the target)"
  else row config "$f" FILE "$(wc -c < "$f" | tr -d ' ') bytes"; fi
done

# --- operator-assisted steps ----------------------------------------------
if [ -f "$HERE/probe-operator.sh" ]; then
  while read -r id; do
    [ -z "$id" ] && continue
    row operator "$id" GUIDED "run one at a time; verify from transcript or user attestation"
  done < <(bash "$HERE/probe-operator.sh" list 2>/dev/null \
           | awk '$1 ~ /^(manual|op)\./ {print $1}')
fi

# --- output ----------------------------------------------------------------
if [ "$TSV" -eq 1 ]; then
  printf '%s\n' "${rows[@]}"
  exit 0
fi

cur=""
for r in "${rows[@]}"; do
  area=$(echo "$r" | cut -f1); item=$(echo "$r" | cut -f2)
  st=$(echo "$r" | cut -f3);   dt=$(echo "$r" | cut -f4)
  [ "$area" != "$cur" ] && { printf '\n%s\n' "$(echo "$area" | tr '[:lower:]' '[:upper:]')"; cur="$area"; }
  printf '  %-22s %-12s %s\n' "$item" "$st" "$dt"
done

cat <<'NOTE'

NOT DETECTABLE FROM THE SHELL
  The agent's own file tools (read/write/edit/notebook) and its web and MCP
  tools cannot be inventoried from here. The agent must check those itself —
  see reference/agent-probes.md.
NOTE
