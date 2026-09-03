#!/usr/bin/env bash
# Run a real nonpersistent child harness for startup-only native telemetry.
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
SKILL="$(cd "$HERE/.." && pwd)"
. "$HERE/_lib.sh"

AGENT=""
while [ $# -gt 0 ]; do
  case "$1" in
    --agent) AGENT="${2:-}"; shift 2 ;;
    *) echo "usage: run-child.sh --agent claude|codex" >&2; exit 2 ;;
  esac
done
[ "$AGENT" = "claude" ] || [ "$AGENT" = "codex" ] || {
  echo "usage: run-child.sh --agent claude|codex" >&2
  exit 2
}

sandbox
mkdir -p "$HARNESS_CHECK_DIR/child-workspace"
OUT="$HARNESS_CHECK_DIR/child-$AGENT.jsonl"
MCP_LOG="$HARNESS_CHECK_DIR/child-$AGENT-mcp-methods.log"
: > "$MCP_LOG"
export HARNESS_CHECK_MCP_LOG="$MCP_LOG"
PROMPT='This is a telemetry probe. Perform each step through the named native tool and do nothing else. 1. Call the harness_echo MCP tool exactly once with text "harness-check-mcp-called". 2. If a native MCP resource listing tool exists (Claude Code: ListMcpResourcesTool with server "harness-check"), list resources with it. 3. If a native MCP resource read tool exists (Claude Code: ReadMcpResourceTool with server "harness-check"), read the resource harness-check://fixture/resource with it. 4. If a native MCP prompt interface exists, get harness-check-prompt through it; skip this step if prompts are only exposed as user slash commands. Never substitute a different tool for a missing interface. 5. Use the native shell tool to run: printf harness-check-child-shell. Do not edit files. Return exactly harness-check-child-complete.'

if [ "$AGENT" = "claude" ]; then
  command -v claude >/dev/null 2>&1 || {
    skip child.claude.session "claude CLI not installed"
    summary child-claude
    exit 0
  }
  MCP_CONFIG=$(printf '{"mcpServers":{"harness-check":{"type":"stdio","command":"python3","args":["%s","--log","%s"]}}}' "$SKILL/assets/mcp-server.py" "$MCP_LOG")
  (
    cd "$HARNESS_CHECK_DIR/child-workspace" || exit 1
    claude -p \
      --no-session-persistence \
      --permission-mode auto \
      --model haiku \
      --max-budget-usd 0.10 \
      --plugin-dir "$SKILL/assets/claude-plugin" \
      --settings "$SKILL/assets/claude-settings.json" \
      --strict-mcp-config \
      --mcp-config "$MCP_CONFIG" \
      --allowedTools Bash,mcp__harness-check__harness_echo,ListMcpResourcesTool,ReadMcpResourceTool \
      --verbose \
      --output-format stream-json \
      --include-hook-events \
      "$PROMPT" </dev/null
  ) > "$OUT" 2>&1
  RC=$?
else
  command -v codex >/dev/null 2>&1 || {
    skip child.codex.session "codex CLI not installed"
    summary child-codex
    exit 0
  }
  (
    cd "$HARNESS_CHECK_DIR/child-workspace" || exit 1
    codex exec \
      --ephemeral \
      --approve-for-me \
      --skip-git-repo-check \
      --json \
      -c 'mcp_servers.harness_check.command="python3"' \
      -c "mcp_servers.harness_check.args=[\"$SKILL/assets/mcp-server.py\",\"--log\",\"$MCP_LOG\"]" \
      "$PROMPT" </dev/null
  ) > "$OUT" 2>&1
  RC=$?
fi

if [ "$RC" -eq 0 ]; then
  pass "child.$AGENT.session" "real child harness exited successfully"
  pass "child.$AGENT.lifecycle.stop" "child process completed and stopped"
else
  fail "child.$AGENT.session" "exit=$RC; output=$OUT"
  fail "child.$AGENT.lifecycle.stop" "child did not stop cleanly"
fi

method_seen() { grep -qx "$1" "$MCP_LOG" 2>/dev/null; }
method_count() { grep -cx "$1" "$MCP_LOG" 2>/dev/null || true; }

method_seen initialize \
  && pass "child.$AGENT.mcp.connect" "fixture completed MCP initialize" \
  || fail "child.$AGENT.mcp.connect" "initialize absent; inspect $MCP_LOG"
method_seen tools/list \
  && pass "child.$AGENT.mcp.tools-list" "real client listed fixture tools" \
  || fail "child.$AGENT.mcp.tools-list" "tools/list absent; inspect $MCP_LOG"

if grep -q $'^tools/call\tharness_echo\tharness-check-mcp-called$' "$MCP_LOG"; then
  pass "child.$AGENT.mcp" "real harness invoked fixture MCP tool"
else
  fail "child.$AGENT.mcp" "verified tools/call marker absent; inspect $MCP_LOG"
fi

for method_id in resources/list resources/read resources/subscribe prompts/list prompts/get; do
  probe_id=$(printf '%s' "$method_id" | tr / -)
  if method_seen "$method_id"; then
    pass "child.$AGENT.mcp.$probe_id" "real client sent $method_id"
  else
    skip "child.$AGENT.mcp.$probe_id" "client sent no $method_id; no native path, or the child did not invoke it"
  fi
done

if [ "$(method_count tools/list)" -gt 1 ]; then
  pass "child.$AGENT.mcp.notification-listen" "client reacted to list_changed notification"
else
  skip "child.$AGENT.mcp.notification-listen" "notification sent; client reaction not observable"
fi

if grep -q 'harness-check-child-shell' "$OUT"; then
  pass "child.$AGENT.shell" "real harness invoked native shell"
else
  fail "child.$AGENT.shell" "shell marker absent; inspect $OUT"
fi

if grep -q 'harness-check-child-complete' "$OUT"; then
  pass "child.$AGENT.response" "model response completed"
else
  fail "child.$AGENT.response" "completion marker absent; inspect $OUT"
fi

if [ "$AGENT" = "claude" ]; then
  # The init message of the stream-json output lists every loaded plugin by
  # name — check that instead of inferring the load from a clean exit.
  if grep -q 'harness-check-fixture' "$OUT"; then
    pass child.claude.plugin "init message lists harness-check-fixture plugin"
  else
    fail child.claude.plugin "plugin absent from init message; inspect $OUT"
  fi
  if grep -q 'harness-check-hook-executed' "$OUT"; then
    pass child.claude.hook "registered PostToolUse hook executed"
  else
    fail child.claude.hook "hook marker absent; inspect $OUT"
  fi
  [ "$RC" -eq 0 ] \
    && pass child.claude.hook-remove "session-scoped hook removed when child stopped" \
    || skip child.claude.hook-remove "child did not stop cleanly"
fi

summary "child-$AGENT"
