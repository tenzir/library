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
| `tool_result` | successful and failing native calls | automatic |
| `skill_activated` | invoking this skill | automatic |
| `subagent_completed` | one real bounded subagent task | automatic when the tool exists |
| `mcp_server_connection` | connect the child Claude session to the bundled fixture server | automatic |
| `permission_mode_changed` | change the live permission mode | user-only interactive control |
| `plugin_loaded` | load a real installed or session-scoped fixture plugin | automatic with `--plugin-dir` in a child Claude session |
| `hook_registered` | start a real child Claude session with a fixture hook configuration | automatic |
| `hook_execution` | trigger that registered hook through its matching native tool | automatic |

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
| `codex.sandbox_outcome` | run shell work through the actual Codex sandbox | automatic |
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

Record unavailable or unconfigured conditional surfaces as gaps. Never claim
coverage from a shell substitute when the event belongs to a native tool.
Never log in, log out, upload data, mutate an account, or call a real configured
MCP server solely to increase coverage.

## Delivery

Treat delivery as a separate required result. Follow
`telemetry-verification.md` and report either verified receipt or the precise
reason verification was unavailable. Exporter configuration alone is not
receipt evidence.
