# Anthropic

Normalize Claude Code OpenTelemetry logs, spans, and selected metrics to
OCSF 1.9.0. Unknown activity remains a Base Event rather than acquiring an
unsupported API or process classification.

## Normalize telemetry

Receive and normalize native records:

```tql
accept_otlp "0.0.0.0:4318", transport="http", schema="record"
where @name in ["otel.log", "otel.span"]
anthropic::claude_code::ocsf::normalize
```

Add the destination operator in your deployment. The package contains operators
and examples, but no pipelines. The schema filter excludes metrics, not Base
Events. Remove it to include the metric mappings described below.

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

## Operator structure

`anthropic::claude_code::canonicalize` prepares native OTLP records and applies
source-specific noise and duplicate filters. Its `event` field argument defaults
to `this`; filtering still applies to the event stream.

`anthropic::claude_code::ocsf::map claude_code, ocsf` consumes a canonical source
field and writes the mapped event to a separate destination field. It leaves
unrelated fields intact and retains source residue in `ocsf.unmapped`.
The dispatcher calls shared context, event-specific mapping, and finalization
operators under `ocsf/`.

`anthropic::claude_code::ocsf::normalize` combines those stages and preserves
`raw_data` and `raw_data_size`. Use it for native receiver records. Its `into`
argument defaults to `this`; set `into=result` to retain the surrounding event
and write OCSF into `result`.

## Tests

Run the package tests from the library root:

```sh
uvx tenzir-test anthropic
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
| Bash decision | Process Activity, 1007 | Launch |
| Foreground Bash result | Process Activity, 1007 | Terminate |
| Result for requested background execution | Process Activity, 1007 | Other: Observe; status Unknown |
| Read with a reported path | File System Activity, 1001 | Read |
| Write, Edit, NotebookEdit with a reported path | File System Activity, 1001 | Update |
| Explicit create, delete, or rename with a reported path | File System Activity, 1001 | Create, Delete, Rename |
| Glob with a search path | File System Activity, 1001 | Other: Search |
| Grep with a search path | File System Activity, 1001 | Read |
| Remote tool decision | API Activity, 6003 | Other: Authorize |
| MCP tool, web search/fetch, or other recognized remote-tool result | API Activity, 6003 | Other: Invoke |
| MCP server connection | API Activity, 6003 | Create |
| Model request, API error, request/response body record | API Activity, 6003 | Create |
| User prompt / assistant response | API Activity, 6003 | Other: Prompt / Respond |
| Auth record with action login | Authentication, 3002 | Logon |
| Permission-mode change | Authorize Session, 3003 | Assign Privileges |
| Plugin installation | Application Lifecycle, 6002 | Install |
| Plugin load, skill activation, hook registration | Application Lifecycle, 6002 | Enable |
| Hook execution start / completion | Process Activity, 1007 | Launch / Terminate |
| API retries exhausted | Application Error, 6008 | General Error |
| File decision without a path, unknown local tool, subagent completion | Base Event, 0 | Other: source event name |

When an API record provides an HTTP method, the mapping uses Read for GET/HEAD,
Create for POST, Update for PUT/PATCH, and Delete for DELETE. Tool names alone
do not imply these actions. A count of API Create events is not a model-call
count because connections and body records also use Create.

### Shell and file outcomes

Shell records emit independently, without a join or five-second wait. Decision
and result records use `anthropic:claude-code:<tool_use_id>` as their
`process.uid`. A denied decision is a failed Launch. Shell commands never
map to Script Activity. The mapper prefers `tool_parameters.full_command`
over potentially truncated `tool_input.command`; it does not invent a PID
or infer `process.created_time` from tool duration.

A background request does not prove that a process is still running or has
finished. Its result stays Observe with Unknown status.
`unmapped.background_requested` and `unmapped.tool_success` preserve the
request and the tool outcome.

Write does not establish that a file is new, so it maps to Update. Glob and
Grep retain their tool name and search pattern. A search path is not assumed
to be a folder; its type is Unknown unless an EISDIR error establishes a folder.
Without a reported target, the file tool stays Base Event.

Deletion sets `file.is_deleted` only for a successful, non-denied operation.
Rename sets `file_result` only on success; otherwise the proposed destination
stays in `unmapped.file_new_path`. With content enabled, successful,
non-denied edits populate `file_diff`. Unapplied edits do not populate it.
Messages distinguish failed, denied, and unknown operations from successful ones.

### Remote calls and conversation

For generic `mcp_tool` records, `tool_parameters.mcp_server_name` supplies
`api.service.name` and `mcp_tool_name` supplies `api.operation`.
Recognized MCP names can also supply that identity. Resource reads and web
fetches retain reported target URIs in `resources`. Local tools do not become
remote calls merely because they have a name.

Remote authorization and invocation remain separate records, correlated through
`api.request.uid`. Claude Code repeats authorization on tool results when
available. The Security Control profile distinguishes user approval from a
named policy decision; the source of the decision is `policy.type`, not an
invented rule name.

Conversation text uses `message_context.prompt_text` or `response_text`
when content is enabled. API Activity is the current fallback for these
records, not a claim that audit-log retrieval is the activity.
`metadata.correlation_uid` uses the reported prompt ID, not the trace ID.
The session is also in `message_context.uid`; a reported prompt ID remains
in `message_context.name` and `unmapped.prompt_id`.

Login retains the source protocol spelling without assuming an OAuth version,
and does not use the conversation ID as an authenticated-session ID. Plugin
installation retains marketplace and trigger in `unmapped`; it does not
infer a vendor from the marketplace. Retry exhaustion retains the attempt
count and total retry duration without creating another model call.

### Filtering and metrics

Tool, tool-execution, approval-wait, model-request, and interaction spans that
duplicate logs are suppressed on native inputs. Feedback survey
events are discarded.

Native `claude_code.session.count` metrics map to Application Lifecycle /
Start. Other retained metrics map to Base Event with their aggregation window
and quantity. Token and cost usage metrics are discarded because API request
logs already report that usage. The receiver example excludes metrics.
