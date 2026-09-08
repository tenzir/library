# Native telemetry coverage

Use this matrix as the completion contract. A probe counts only when Claude
Code or Codex itself performs the action and emits its normal telemetry. Test
fixtures are valid targets; fabricated telemetry and direct protocol drivers
are not.

## Claude Code

| Native OTEL event or span | Real trigger | Interaction |
| --- | --- | --- |
| `user_prompt` | invoking this skill and later user replies | automatic |
| `api_request` | every model turn | automatic |
| `assistant_response` | every completed model turn | automatic |
| `claude_code.interaction` | a normal model/tool interaction | automatic |
| `tool_decision` | each real native tool call; include allowed and denied decisions | automatic except the user's allow/deny choice |
| `tool_decision` (hook source) | run the `harness-check-hook-deny` marker in the child; its PreToolUse fixture hook denies it | automatic |
| `tool_decision` (config source) | run the `harness-check-config-deny` marker in the child; a `permissions.deny` rule blocks it | automatic |
| `tool_result` | successful and failing native calls | automatic |
| `skill_activated` | invoking this skill | automatic |
| `subagent_completed` | one real bounded subagent task | automatic when the tool exists |
| `mcp_server_connection` | connect the child Claude session to the bundled fixture server | automatic |
| `permission_mode_changed` | call EnterPlanMode then ExitPlanMode; only modes the agent cannot set need the interactive control | automatic for plan, user-only for the rest |
| `user` records wrapping `<bash-input>`/`<bash-stdout>` (shell typed with `!`) | the user types a `!`-prefixed shell command | user-only interactive control |
| `plugin_loaded` | load a real installed or session-scoped fixture plugin | automatic with `--plugin-dir` in a child Claude session |
| `hook_registered` | start a real child Claude session with the fixture hook configuration | automatic |
| `hook_execution_start` / `hook_execution_complete` | the child fires PreToolUse, PostToolUse, UserPromptSubmit, SessionStart, SessionEnd, Stop, plus best-effort PreCompact and Notification fixture hooks; the hook log proves which fired | automatic, PreCompact and Notification conditional |
| `api_error` | a child whose API base URL points at a closed loopback port; the first model request fails to connect | automatic, no credential sent |
| `user_prompt` / `tool_decision` content shapes | the child repeats a trivial turn with prompt and tool-detail logging redacted and then verbose | automatic |
| `retention_sweep` | context compaction, reached only if the session compacts | conditional; the PreCompact hook marks it best-effort |
| cost, token-usage, session-count, lines-of-code, code-edit, and commit metrics | emitted on the natural session activity; enhanced telemetry and a metric exporter must be enabled | automatic startup/interval observation |
| `log_format` = `OTLP/gRPC` \| `OTLP/HTTP` \| `OTLP/JSON` | run the child once per transport with `run-child --transport grpc\|http\|json`; a run emits only its selected transport | conditional, one transport per run |
| session resume | the child persists a fixed session id, then a second `--resume` reopens it | automatic when persistence is available |

## Codex

| Native OTEL event, metric, or span | Real trigger | Interaction |
| --- | --- | --- |
| `codex.conversation_starts` | this session or an ephemeral child session | automatic |
| `codex.user_prompt` | invoking this skill and later user replies | automatic |
| `codex.websocket_connect` / `codex.websocket_request` | normal model transport | automatic when that transport is selected |
| `codex.api_request` | every model turn | automatic |
| completed `codex.sse_event` | every completed response | automatic when SSE is selected |
| `session_task.turn` | complete a turn | automatic |
| `codex.tool_decision` | each native tool call; include allowed and denied decisions | automatic except the user's allow/deny choice |
| `codex.tool_result` | successful and failing native calls | automatic |
| `codex.sandbox_outcome` | run shell work through the actual Codex sandbox; vary it with `run-child --sandbox read-only\|workspace-write\|danger-full-access` for distinct outcomes | automatic, one policy per run |
| `codex.skill.injected` | invoking this skill | automatic |
| `codex.tool.call` | native tool calls | automatic |
| `list_tools_for_server` | let the child Codex session discover the bundled fixture server | automatic |
| `config/batchWrite` | change persistent config through the Codex UI/API | user-only if the current harness exposes that control |
| `built_tools` | start with connected apps enabled | automatic startup observation |
| `plugins_for_config` | start with actual plugins enabled | automatic startup observation |
| `recommended_plugins_mode_for_config` | start with remote-plugin policy configured | automatic startup observation |

Transport-specific events are conditional, not failures: a WebSocket run does
not also emit an SSE completion. Startup observations reflect real resolved
configuration and must not be simulated by writing similarly shaped files.

The `!`-shell row is a transcript record, not a confirmed OTEL event.
Observed in Claude Code 2.1.245, a `!`-typed command lands in two `user`
records (`isMeta: false`) wrapping `<bash-input>` and `<bash-stdout>`, and no
`system`/`local_command` subtype appears — so record the transcript surface
it actually reaches, and report a missing OTEL event as a finding, not a
probe failure.

## Tool activity

Exercise each native tool family that the current harness actually exposes:

- file read, create, update, delete, rename, search, image/PDF/notebook access,
  and an expected missing-file or no-match failure;
- shell command success, nonzero exit, environment access, live-session input,
  child launch, background execution, termination, and sandbox denial;
- web search and fetch, plus shell network separately;
- model requests, discrete conversation turns, and safe read-only vendor auth,
  account, or quota calls when exposed;
- fixture MCP initialize, tools/resources/prompts listing, resource read,
  prompt get, subscription/notification channel, and tool invocation by a real
  isolated child harness;
- skill/plugin lifecycle, subagent lifecycle, session start/stop/resume/restart,
  hook registration/removal/firing, and scheduler create/update/delete/
  enable/disable/start;
- an approval accepted and an approval declined.

## Security-relevant shapes

`probe-security.sh` generates harmless, sandbox-confined commands whose
STRUCTURE matches techniques an OCSF detection is meant to flag: credential
and private-key reads, single-variable environment capture, base64
decode-and-execute, download-and-run and chmod-then-execute against a
loopback HTTP fixture, a `.git/hooks` implant, an agent editing its own
`.claude`/`.codex` configuration, a gated `sudo`, package-install attempts,
and a `git push` to a local bare remote. The loopback fixture logs every
request it serves, so egress is verifiable without leaving the host. These are
real shell events with security-relevant shape, not fabricated telemetry; none
carries a real secret or reaches the internet.

Record unavailable or unconfigured conditional surfaces as gaps. Never claim
coverage from a shell substitute when the event belongs to a native tool.
Never log in, log out, upload data, mutate an account, or call a real configured
MCP server solely to increase coverage.

## Delivery

Treat delivery as a separate required result. Follow
`telemetry-verification.md` and report either verified receipt or the precise
reason verification was unavailable. Exporter configuration alone is not
receipt evidence.
