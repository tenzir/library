# OpenAI

Normalize security-relevant Codex OpenTelemetry logs, spans, and selected metrics
to OCSF 1.9.0. Service names beginning with `codex` identify supported clients,
including `codex_cli_rs`, `codex_exec`, and `codex-app-server`.

## Normalize telemetry

Receive native record events and publish them to the `otlp` topic:

```tql
accept_otlp "0.0.0.0:4318", transport="http", schema="record"
publish "otlp"
```

Run this separately to normalize logs and spans:

```tql
subscribe "otlp"
where @name in ["otel.log", "otel.span"]
openai::codex::ocsf
ocsf_derive
ocsf_cast
publish "ocsf"
```

The schema filter excludes metrics, not Base Events. Remove it if you also want
the metric mappings described below. The packaged OCSF publishing pipeline
accepts metrics; the ClickHouse pipeline excludes them.

Install this vendor package only; no shared `otel` package is required.
Input must be native records from `accept_otlp` with `schema="record"`.
Saved OTLP/JSON export envelopes are not supported.

## Content and identifiers

The default `include_content=false` omits copied prompt, response, and tool-input
text from normalized content fields. Hashes remain where the source supplies
the corresponding content. Set `include_content=true` to populate conversation
text in `message_context` and parsed remote-tool input in `api.request.data`.

**This option does not redact `raw_data`.** The complete input record remains
there. Shell commands are always retained in `process.cmd_line`, regardless
of this option. Review access and retention policies before storing either.

The mapping preserves these identifiers when the source supplies them:

| Identifier | Destination |
| --- | --- |
| Source event name | `metadata.event_code` |
| Session ID | `actor.session.uid`; also `ai_agent.instance_uid` where the AI Operation profile applies |
| Tool-call ID | Prefixed `process.uid` for shell lifecycle, `api.request.uid` for remote calls, otherwise `unmapped.tool_use_id` |
| Trace ID | `trace.uid` on branches using the Trace profile, otherwise `unmapped.trace_id` |
| Log's enclosing span ID | `unmapped.span_id`, even when the log has `trace.uid` |
| Complete span's ID and parent | `trace.span.uid` and `trace.span.parent_uid` on branches using the Trace profile |
| Source span record ID | `metadata.original_event_uid`; logs do not receive an invented record ID |

A log does not provide the enclosing span's lifetime, so it does not create a
`trace.span` object. Root spans may omit their parent and status message.
Unmapped span context stays available on classes without a trace destination.

Discrete tool runtimes stay in `unmapped.duration_ms`. Complete mapped spans
use `trace.span.start_time`, `end_time`, and `duration`. Top-level
`start_time`, `end_time`, and `duration` describe aggregate windows, not
individual tool runtimes.

## Store events in ClickHouse

The packaged ClickHouse pipeline is disabled by default. Configure these
secrets before enabling it:

- `CLICKHOUSE_HOST`
- `CLICKHOUSE_USERNAME`
- `CLICKHOUSE_PASSWORD`

The `clickhouse_database` package input defaults to `ocsf`. The pipeline
uses TLS and appends to `<database>.events`. All retained classes, including
Base Event, share the table. Metrics are excluded before normalization.

Frequently queried fields are columns; the complete mapped event is the JSON
column `event`. Its nested `unmapped` fields remain JSON fields, not an
encoded JSON string. The indexed `app_name` comes from
`actor.application.name`. The operator's existing noise and duplicate-span
filters still apply.

## Tests

Run the package tests from the library root:

```sh
uvx tenzir-test openai
```

Fixtures distinguish captured records from synthetic edge cases. Tests cover
file outcomes, command lifecycle, remote calls, trace-context retention, and
missing optional fields. They do not imply that the live collector has been
updated to this package version.

## Activity mappings

These are the current package mappings, not proposed AI-specific classes.
An activity labeled Other has `activity_id=99` and the displayed label in
`activity_name`.

| Source record or tool | OCSF class | Activity |
| --- | --- | --- |
| Shell tool decision | Process Activity, 1007 | Launch |
| Shell result with a parsed exit code and no running marker | Process Activity, 1007 | Terminate |
| Running shell result or result without a confirmed exit | Process Activity, 1007 | Other: Observe; status Unknown |
| Code Mode exec span | Process Activity, 1007 | Provisional Launch |
| Recognized file operation with a path | File System Activity, 1001 | Read, Create, Update, Delete, Rename |
| Remote tool decision | API Activity, 6003 | Other: Authorize |
| MCP or web tool result | API Activity, 6003 | Other: Invoke |
| MCP hook span with hook server and tool | API Activity, 6003 | Other: Invoke |
| MCP tool discovery, list_tools_for_server | API Activity, 6003 | Read |
| Configured plugin/application posture observations | API Activity, 6003 | Read |
| Model request or websocket setup | API Activity, 6003 | Create |
| User prompt / completed response / turn span | API Activity, 6003 | Other: Prompt / Respond / Turn |
| JSON-RPC operation | API Activity, 6003 | Other: Call |
| HTTP record with method and server address | HTTP Activity, 4002 | Corresponding HTTP method |
| Conversation start posture | Authorize Session, 3003 | Assign Privileges |
| Skill injection | Application Lifecycle, 6002 | Enable |
| Sandbox outcome | Base Event, 0 | Other: Sandbox Outcome |
| write_stdin, unknown local tool, file decision without a path | Base Event, 0 | Other: source event name |
| Recognized command argument-validation failure | Base Event, 0 | Other: source event name; Failure |

For API records with an HTTP method, the mapping uses Read for GET/HEAD,
Create for POST, Update for PUT/PATCH, and Delete for DELETE. JSON-RPC and
tool names alone do not imply read/write intent. API Create counts include
websocket setup, so they are not a count of model calls.

### Shell and file outcomes

Shell decisions and results emit independently, without a join or five-second
wait. They share `openai:codex:<call_id>` as `process.uid` when a call ID is
available. A denied decision is a failed Launch. Shell commands never map to
Script Activity. Compound shell commands stay intact in `process.cmd_line`.
Neither a PID nor `process.created_time` is inferred.

Tool success does not establish command success. For `exec_command`, the
mapper reads the result envelope's `Process exited with code N` marker.
Zero means Success and a nonzero code means Failure; the code populates
`exit_code` and `status_code`. A running marker or an absent, empty, or
unrecognized completion envelope produces Observe with Unknown status.
The producer's success flag remains in `unmapped.tool_success`.

A recognized `failed to parse function arguments:` result stays Base Event /
Failure because argument validation does not establish process execution.
A command printing that text inside a successful result is not misclassified.

Later `write_stdin` calls remain separate tool interactions. Their terminal
session ID can relate them to an earlier command, but the package does not
maintain a long-lived session join or reuse the original call ID.

An `apply_patch` result produces one event per affected file.
`*** Add File:` maps to Create; generic Write maps to Update.
Deletion sets `file.is_deleted` only for a successful, non-denied operation.
A successful rename populates `file_result`; otherwise its proposed
destination stays in `unmapped.file_new_path`. Messages distinguish failed,
denied, and unknown outcomes from successful changes.

### Remote calls and conversation

MCP identity can come from an explicit server field, a complete
`mcp__<server>__<tool>` name, or separate tool namespace and name fields.
The server goes to `api.service.name`, the operation to `api.operation`,
and the call ID to `api.request.uid`. A malformed name does not invent a
server. Web namespace operations keep their namespace, such as `web.run`.

Parsed arguments populate `api.request.data` when content is enabled.
MCP resource reads and URLs opened by a combined web call also populate
`resources`. One combined web call is not split into invented invocations.

A `codex.hooks.mcp_tool` span requires both `hook.server` and `hook.tool`
for the remote mapping. It retains actual trace timing and
`unmapped.hook_timeout_sec`, without inventing success or a call ID.
Incomplete identities fall back to Base Event.

Remote decisions use Authorize and results use Invoke, joined by
`api.request.uid`. The result does not inherit an earlier decision through
aggregation. The Security Control profile retains reported authorization and
its source in `policy.type`, not an invented rule name.

Conversation records remain separate from model calls. API Activity is the
current fallback, not a claim that audit-log retrieval is the activity.
`metadata.correlation_uid` uses a reported prompt ID, otherwise a turn ID;
it never substitutes the trace ID. The session is also in
`message_context.uid`. Reported prompt IDs remain in
`message_context.name` and `unmapped.prompt_id`.
Websocket request and completed-response logs are not merged.

### Filtering and metrics

Internal HTTP/2 and async-runtime spans, metric-like logs, and duplicate native
tool spans are filtered. Code Mode exec and explicitly identified MCP hook
spans retain their separate mappings. Unknown local tools remain Base Events.

Native `codex.skill.injected` metrics map to Application Lifecycle / Enable.
`codex.tool.call` metrics remain Base Events with their aggregate count,
window, and sandbox context; they are not individual invocations. Other
metrics are filtered. The ClickHouse pipeline excludes all metrics.
