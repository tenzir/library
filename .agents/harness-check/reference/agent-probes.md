# Native agent probes

Run every applicable probe through the current harness's native tool. Resolve
`$HARNESS_CHECK_DIR/fixtures` to absolute paths first. Append outcomes with
`python3 scripts/harness_check.py record PASS|FAIL|SKIP <id> <detail>`.

The calls below generate real harness telemetry. Do not replace a missing
native capability with shell, and do not drive MCP protocol messages directly.

## Files and search

Use native read/view, edit/patch, and search tools:

1. `native.file.read`: read `plain.txt`.
2. `native.file.read-window`: read only lines 100–104 of `long.txt`.
3. `native.file.read-missing`: request `does-not-exist.txt`; pass when the real
   native call returns an error.
4. `native.file.search-name`: find `plain.txt` by filename.
5. `native.file.search-content`: find `harness-check-sentinel-42` by content.
6. `native.file.create`: create `native-created.txt` through the native write
   or patch tool.
7. `native.file.update`: update that file through the native edit or patch
   tool, then read it back.
8. `native.file.rename`: rename a disposable file through a native file tool
   when the harness exposes one. Do not count shell `mv` as native coverage.
9. `native.file.delete`: delete a disposable file through a native file tool.
   For Codex, an `apply_patch` delete is native deletion coverage.
10. `native.file.edit-missing`: request an edit with an absent match; pass when
   the native tool refuses it.
11. `native.file.image`: view `pixel.png` through the native image/read tool.
12. `native.file.pdf`: read `doc.pdf` through a native PDF-capable tool.
13. `native.file.notebook`: read and edit one cell in `notebook.ipynb` through
    a structured notebook tool, then restore it.

For Codex, `apply_patch` and `view_image` are native. Shell reads and `rg` are
shell telemetry, not native file/search telemetry. For Claude Code, use
`Read`, `Write`, `Edit`, `Glob`, `Grep`, and `NotebookEdit` when present.

## Command and process boundary

Use the native command tool for distinct calls so each gets its own decision
and result:

1. `native.shell.success`: `printf harness-check-shell-success`.
2. `native.shell.failure`: run a command that exits 23.
3. `native.shell.environment`: read only a new harmless variable set for that
   invocation; do not dump the environment.
4. `native.shell.background`: start a two-second background process, observe
   it, and wait for completion using the harness's background/session support.
5. `native.shell.stdin`: start a live command that waits for one line, send
   `harness-check-stdin` through the harness's native session-input control,
   and verify that the command received it.
6. `native.process.launch`: start a disposable 30-second child through the
   native command/session tool and observe its live session or PID.
7. `native.process.terminate`: terminate that exact child through the native
   task-stop/session control and observe its non-clean completion.
8. `native.shell.timeout`: time out a sleeping child.
9. `native.shell.sandbox-denial`: attempt a harmless write outside the allowed
   workspace without escalation and pass when the sandbox denies it. Do not
   target a pre-existing file.

The bundled shell scripts additionally generate dense syscall/process/file
workloads inside one command invocation; these native calls cover the harness
decision/result boundary itself.

## Web and network

1. `native.web.search`: search for the current OpenTelemetry home page through
   the harness's web-search tool.
2. `native.web.fetch`: fetch `https://example.com` through the native fetch or
   browser tool.
3. Keep the shell `curl` result from `probe-cli.sh` separate: native web and
   sandboxed shell egress are different security boundaries.

## Agent-vendor APIs and authentication

- Model requests and discrete user/assistant turns occur naturally while this
  skill runs. Record the trigger, but do not merge the turn with its model call.
- Run the installed product's read-only authentication-status command. Never
  print tokens or credentials.
- When a native, already-authorized account or quota read is exposed, invoke it
  once and record `native.vendor.account-read` or `native.vendor.quota-read`.
- Record account create/update/delete, uploads, login, and logout as `SKIP`
  unless the harness provides a disposable test tenant or fixture explicitly
  authorized for mutation. Do not alter the user's real account merely for
  telemetry.

## MCP

Do not discover or invoke MCP servers from the user's existing configuration.
Always run the isolated child-session fixture described in
`child-sessions.md`. The real child harness must initialize the server, list
tools, and invoke `harness_echo`. The fixture also advertises resources,
prompts, subscriptions, and list-changed notifications. Exercise those native
protocol paths when the client exposes them; otherwise record each exact
method as `SKIP`. Never count direct execution of `assets/mcp-server.py` as
MCP coverage.

Use ids `child.claude.mcp` or `child.codex.mcp`.

## Skills, subagents, and schedulers

- `native.skill.activated` is implicit because this skill is running; record
  it without invoking another skill solely for telemetry.
- When the harness exposes subagents, run one bounded child that returns
  exactly `harness-check-subagent`, wait for it, and record
  `native.subagent.complete`.
- When the harness exposes a native scheduler, create a disposable recurring
  task whose only action writes a sentinel beneath `$HARNESS_CHECK_DIR`.
  Inspect, update, disable, enable, and delete it. Use a native run-now control
  to make it fire and verify the sentinel. If run-now is unavailable, use the
  shortest safe schedule only when it fires within 60 seconds; otherwise
  record `native.scheduler.start` as `SKIP`. Do not use staged cron files as
  scheduler coverage.

## Session lifecycle

- The isolated child covers session start and stop.
- If the product exposes safe noninteractive persistence, create one
  disposable persisted child session, capture its exact session ID, resume it
  once with a sentinel prompt, and remove only the session artifact created by
  the probe when its location can be resolved exactly.
- Use a real restart control when exposed. A second unrelated process start is
  not a restart. Record resume or restart as `SKIP` when the product lacks a
  safe disposable path.

## Startup-only events

Read `child-sessions.md` and automatically run the applicable real child
harness once. Skip only when the CLI, authentication, telemetry export, or a
safe noninteractive mode is unavailable.
