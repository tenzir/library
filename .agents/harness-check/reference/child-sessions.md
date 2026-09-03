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

When `claude` is installed, run one non-persistent child session with:

- `--no-session-persistence`;
- `--permission-mode auto`;
- `--model haiku --max-budget-usd 0.10` to keep the fixture turn cheap;
- `--plugin-dir <skill>/assets/claude-plugin`;
- `--settings <skill>/assets/claude-settings.json`;
- `--strict-mcp-config --mcp-config` containing a stdio server whose command is
  `python3` and whose only argument is `<skill>/assets/mcp-server.py`;
- `--allowedTools Bash,mcp__harness-check__harness_echo`;
- a prompt that calls `harness_echo` once, runs
  `printf harness-check-child-shell`, and attempts native resource/prompt
  access when the installed client exposes those interfaces.

Use `-p --output-format stream-json --include-hook-events`. This generates the
real plugin-load, hook-registration, hook-execution, MCP-connection,
tool-decision, tool-result, model, and response paths. Record a skip if the
installed version rejects a flag or authentication is unavailable; do not
fall back to driving the MCP server directly.

## Codex

When `codex` is installed, run one ephemeral child with `codex exec
--ephemeral --approve-for-me --skip-git-repo-check`. Add the MCP
server with per-invocation `-c` overrides:

```text
mcp_servers.harness_check.command="python3"
mcp_servers.harness_check.args=["<skill>/assets/mcp-server.py"]
```

Prompt it to call `harness_echo` once, run
`printf harness-check-child-shell`, attempt native resource/prompt access when
exposed, and return. Do not use
`--ignore-user-config`: startup observations for the user's real enabled apps,
plugins, remote-plugin posture, approval policy, and sandbox policy are part
of the workload. The overrides must not write the user's config.

Do not run a child session when it would prompt for login, consume an
unexpected paid provider, or require an approval that the parent cannot safely
handle. Record the exact gap instead.
