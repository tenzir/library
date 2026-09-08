# Real child harness sessions

Run `python3 scripts/harness_check.py run-child --agent claude|codex`. Use a
child session only
for startup-time telemetry that the current session
cannot emit retroactively. These are real Claude Code or Codex clients. The
bundled MCP server and Claude plugin are disposable targets, not telemetry
simulators: the child harness must discover, connect to, and invoke them.

Resolve the skill directory to an absolute path and preserve inherited OTEL
export environment variables. Do not set a temporary home that loses the
user's existing agent authentication.

The script stores the real client's JSON stream and the fixture's received MCP
method log beneath `$HARNESS_CHECK_DIR`. The method log proves which protocol
operations the real client actually sent; it does not drive the protocol.

## Claude Code

When `claude` is installed, `run-child --agent claude` runs one child session
with:

- a fixed `--session-id` so a later `--resume` can reopen it (falling back to
  `--no-session-persistence` only when no id is used);
- `--permission-mode auto`;
- `--model haiku --max-budget-usd 0.10` to keep the fixture turn cheap;
- `--plugin-dir <skill>/assets/claude-plugin`;
- `--settings` pointing at a run-local copy of
  `<skill>/assets/claude-settings.json` with `__SKILL__` resolved to the
  absolute skill path. That settings file registers PreToolUse, PostToolUse,
  UserPromptSubmit, SessionStart, SessionEnd, Stop, and SubagentStop fixture
  hooks and a `permissions.deny` rule;
- `--strict-mcp-config --mcp-config` containing a stdio server whose command is
  `python3` and whose only argument is `<skill>/assets/mcp-server.py`;
- `--allowedTools Bash,WebFetch,mcp__harness-check__harness_echo,`
  `ListMcpResourcesTool,ReadMcpResourceTool`;
- a prompt that calls `harness_echo` once, runs `printf
  harness-check-child-shell`, then runs the `harness-check-hook-deny` and
  `harness-check-config-deny` markers (denied by the fixture hook and the deny
  rule) and `harness-check-hook-fail` (which runs but trips a failing
  PostToolUse hook), attempts native resource/prompt access, and fetches the
  bundled loopback HTTP fixture when a web tool is exposed.

Use `-p --output-format stream-json --include-hook-events`. This generates the
real plugin-load, hook-registration, hook-execution (start and complete),
hook- and config-sourced tool denials, MCP-connection, tool-decision,
tool-result, model, and response paths. Two side logs make receipt verifiable
without trusting the transcript: the MCP method log and the hook-event log
(`HARNESS_CHECK_HOOK_LOG`, one `<event>\t<tool>\t<outcome>` line per firing).
The loopback fixture's request log proves the native fetch reached it.

After a successful run, the driver reopens the persisted session once with
`--resume` and a sentinel prompt to generate real session-resume telemetry,
then leaves the session artifact for the harness to expire. It then runs two
short extra children: one whose API base URL points at a closed loopback port,
so the first model request fails and drives the `api_error` path without
sending a usable credential anywhere reachable; and one trivial turn repeated
with `OTEL_LOG_USER_PROMPTS` and `OTEL_LOG_TOOL_DETAILS` first redacted and
then verbose, so both content shapes appear in one run. The settings fixture
also registers PreCompact and Notification hooks; these fire only if the
session compacts or raises a notification, so a miss is recorded as a skip.

Transport is conditional: pass `run-child --transport grpc|http|json` to force
`OTEL_EXPORTER_OTLP_PROTOCOL`, since one run emits only its selected
transport's completion. Record a skip if the installed version rejects a flag
or authentication is unavailable; do not fall back to driving the MCP server
directly.

## Codex

When `codex` is installed, run one ephemeral child with `codex exec
--ephemeral --approve-for-me --skip-git-repo-check`. Add the MCP
server with per-invocation `-c` overrides:

```text
mcp_servers.harness_check.command="python3"
mcp_servers.harness_check.args=["<skill>/assets/mcp-server.py"]
```

Prompt it to call `harness_echo` once, run
`printf harness-check-child-shell`, create then delete a file through
`apply_patch` for native file-lifecycle coverage, attempt native
resource/prompt access when exposed, and return. Vary the sandbox with
`run-child --sandbox read-only|workspace-write|danger-full-access` to produce
distinct `codex.sandbox_outcome` values across runs. Do not use
`--ignore-user-config`: startup observations for the user's real enabled apps,
plugins, remote-plugin posture, approval policy, and sandbox policy are part
of the workload. The overrides must not write the user's config.

Do not run a child session when it would prompt for login, consume an
unexpected paid provider, or require an approval that the parent cannot safely
handle. Record the exact gap instead.
