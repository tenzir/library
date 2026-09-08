---
title: Normalize Claude Code OTLP telemetry
type: feature
authors:
  - philip
components:
  - anthropic
created: 2026-07-29T00:00:00Z
---

The Anthropic package now normalizes Claude Code OTLP logs, metrics and traces
and maps them directly to OCSF 1.9.0. Agent-mediated activity uses the AI Operation
profile and its `ai_agent` object, including the Claude Code session, runtime
version, and backing model when available.

Use `accept_otlp "0.0.0.0:4318", schema="record"` to receive telemetry and
publish its native `otel.log` and `otel.span` events to the `otlp` topic. The
`anthropic::claude_code::ocsf` operator consumes native record events directly,
where OTLP attributes are already record fields. Legacy OTLP/JSON export
envelopes remain available through
`anthropic::claude_code::ocsf_legacy_envelope`.

The mapping recognizes API and model activity, interactions, permission-mode
changes, MCP server connections, plugin and hook lifecycle events, shell
commands, and file operations. Potentially sensitive prompt, response, and
copied tool content is hashed unless `include_content=true` is explicitly set.
Shell command text is always retained in `process.cmd_line`.
Fields with an OCSF destination are removed from `unmapped`; the complete
native OTLP event remains available in `raw_data`.

An optional pipeline writes mapped activity to a single `events` table in
ClickHouse using the `CLICKHOUSE_HOST`, `CLICKHOUSE_USERNAME`, and
`CLICKHOUSE_PASSWORD` secrets, defaulting to the `ocsf` database. Rather than
one wide table per OCSF class, every class shares one table: a fixed set of
first-class columns carries the fields worth indexing, and the complete event
lands in a ClickHouse `JSON` column named `event`. Optional columns are cast
explicitly, so the table shape does not depend on which class arrives first,
and events from different classes and products stay directly comparable in a
single query. Unmapped events are ignored.

Feedback survey events are discarded because they do not add security context.

The OCSF mapping names explicit remote tool invocations as `Other` with
`Invoke` in `activity_name`; `api.operation` carries the tool name as an
interim home until the `ai_tool` object from ocsf/ocsf-schema#1729 lands. An unknown
tool name alone is not evidence of a remote call and falls back to Base Event.
Typed local file and process records keep their specific classes. Model
calls, including a failed one (`api_error`) and the request and response body
records, and MCP connections are `Create`, so counting `Create` counts model
calls. A conversation turn is not an API call: a user prompt is `Other` with
`Prompt` and an assistant response `Other` with `Respond`, which is also what
`message_context.ai_role` says about them. Other API activity uses an HTTP
verb. Guessing read/write intent from the
shape of a name would misclassify a tool such as `cleanup_stale_records` as a
read.
File tools map from the path the result reports: `file_path` on `Read`,
`Write` and `Edit`, and `notebook_path` on `NotebookEdit`, whose cell edits
are updates of the notebook file. `Write` is always `Create` because the
source does not say whether the path existed before. A read of a path that
does not exist stays a Failure but is rated Informational, since probing for
a file is a normal step for an agent and not a fault. With
`include_content=true` an `Edit` keeps the text it replaced and the text it
wrote in `file_diff`. The file type is `Regular File` unless a read failed
with `EISDIR`, the one case where the operating system reported a folder. A
file-tool decision reports no path at all, so it stays a Base Event with the
decision and the tool name; the result that follows carries the path and
repeats the decision. The `Artifact` tool publishes a local page to claude.ai
or reads one back, so it is a remote call rather than a file operation: an
API Activity `Invoke` with the artifact URL as a target resource when the
call names one. `Glob` and `Grep` read the files under their search root:
when the call names that root, the event is a File System Activity `Read` of
the folder, typed as such, with the pattern in `unmapped.search_pattern`.
Without a root the tool searches the working directory, which the record does
not state, so the call stays a Base Event.

`metadata.original_event_uid` prefers
identifiers that are
unique per event, because `span_id` identifies the enclosing span and is shared
by every record emitted inside it; the span itself is preserved as described
below. A denied tool call is rated `Low` instead of
`Informational`. Normalization artifacts no longer leak into `unmapped`:
`signal` and `transport` are internal, and `decision_source` lands in the
Security Control `policy` and `authorizations[].policy.type`.
Envelope input reports `metadata.log_format` as `OTLP/JSON`.

`message` carries a human-readable summary of each event (for example
"Agent called the model", "Tool call Bash denied") instead of repeating the raw event name, which stays available in
`metadata.event_code`.

Span identifiers are preserved where the schema has no home for them. The Trace
profile applies only to API Activity and HTTP Activity, so on every other class
`span_id` and `parent_span_id` land in `unmapped` rather than being discarded;
`trace_id` is available as `metadata.correlation_uid`.

`metadata.original_event_uid` holds the identifier the source assigned to the
record itself, which is what traces an event back to the raw entry. Only spans
carry one, so it is set from `span_id` for span-sourced events and left empty
for logs and metrics, which have none. A tool-call id such as `tool_use_id` names the
call rather than the record, and the span, the decision and the result all
share it, so it stays on `process.uid` and `api.request.uid`, and
in `unmapped` on classes with no typed home for it.

`metadata.correlation_uid` always identifies the trace, so grouping by it never
mixes a single transaction with a whole session. Events whose source carries no
trace leave it empty; the session is available as `ai_agent.instance_uid`, and
on classes with an actor also as `actor.session.uid`.

Claude Code shell tools map to one Process Activity lifecycle. A Bash decision
is `Launch`; a completed foreground result is `Terminate`. Both derive a
stable `process.uid` from `tool_use_id`, with an `anthropic:claude-code:`
prefix. `process.pid` stays empty because the source does not report an
operating-system PID. The mapper prefers `tool_parameters.full_command` because
Claude can truncate `tool_input.command`.

No correlation window is required. Each lifecycle record emits immediately
and uses the same UID, including commands that run for several minutes. A
denied decision produces a failed Launch without a Terminate. A background
result reports that the launched process is still running, so it stays in
Process Activity as `Other` with `Observe` in `activity_name`, under the same
`process.uid` and with the full command in `process.cmd_line`. It is neither
a second Launch nor a Terminate, and its status is `Unknown` because the
source's `success` flag describes delivery of the observation, not the
outcome of the process.

Spans are suppressed, on the native and the legacy envelope path alike. Every
Claude Code span repeats a log record: the decision and result logs already
report each tool call with its outcome and duration, and the `api_request`,
`api_error`, `user_prompt` and `assistant_response` logs report each model
call and turn together with the prompt id and the cost, which the
`claude_code.llm_request` and `claude_code.interaction` spans lack. What only
a span carries (time to first token, attempt number, stop reason, the
approval wait) is not security relevant, and current versions report neither
a tool name nor a tool-call id on the `tool.execution` and
`tool.blocked_on_user` spans, so they cannot be tied to the call they belong
to. Mapping the spans would only add one to three duplicate events per call.

Metric points map to Base Event. Active time, lines of code, session starts
and code-edit tool decisions are aggregates the agent computed over one export
interval, and OCSF 1.9 has no class for them. Each point keeps its window in
`start_time`, `end_time` and `duration`, its value and unit in `unmapped`, and
its attributes such as the model and the query source. `count` is filled only
for the metrics that count occurrences, session starts and code-edit
decisions. A code-edit decision point carries `decision` and `source`, so it
also carries the Security Control profile. The token and cost usage metrics
are dropped: every `api_request` log already carries the same token counts
and the cost per request, so they would report the same numbers twice. Legacy
OTLP/JSON envelopes still discard metrics.

A model call is two records that share `request_id`: the `api_request` log
is the call itself, API Activity `Create` with the Agent role, and the
`assistant_response` log is the model's reply, `Other` with `Respond` and
the Assistant role. The two are never merged. The call keeps the cost, the
cache token counts, the query source, the effort and the subagent name in
`unmapped`, since OCSF `message_context` has fields for prompt, completion
and total tokens only.

Hooks and subagents are local, not API calls. A hook run is the harness
executing one or more local commands, so `hook_execution_start` is a Process
Activity Launch and `hook_execution_complete` a Terminate, with the hook
group's name in `process.name`. The source reports no command line, PID or
execution id, so `process.cmd_line` is the empty string and `process.uid`
stays empty. A hook registration wires a command into the agent's lifecycle
for the session, the same capability change as a plugin or skill being
enabled, so it is Application Lifecycle `Enable` naming the lifecycle event
and matcher. A finished subagent is a local agent run with no class of its
own and falls back to Base Event, which names the subagent type and the
outcome. Hook records retain their attributes: the hook event, source, type
and matcher on registration, and the hook count and the success, blocking,
error and cancelled counts on completion. A completed hook run is a success
when no hook errored or was cancelled; a blocking hook did its job and is not
a failure of the run.

Tool decisions carry the Security Control profile, which makes an autonomous
action distinguishable from a supervised one. A rule that fires reports
`Allowed`/`Allowed` or `Denied`/`Blocked` in `action_id` and `disposition_id`
with the rule named in `policy`, while a person's decision reports
`Allowed`/`Approved` or `Denied`/`Rejected`. Claude Code repeats the decision
on the tool result and on the blocked-on-user span, so the completed action
itself carries the same profile without a cross-event join. A decision without
a named decider, which Claude Code reports as source `unknown`, keeps an
`Unknown` disposition rather than implying that a rule fired. The
`Unauthorized` disposition stays unused
because the telemetry cannot distinguish a failed permission check from a
policy block. Remote tool decisions stay API Activity `Other`, keep the tool
name in `api.operation` and the MCP server in `api.service.name`, but carry
`Authorize` rather than `Invoke` in `activity_name`: the decision authorizes
a pending call, and the result record is what reports the invocation as
`Invoke`. The two labels keep one call from counting as two invocations, and
both records emit independently however far apart they arrive, joined by
`api.request.uid`. Local shell decisions map to the Process Activity launch
request they govern. The provisioning source (`tool_source`) stays in
`unmapped` because OCSF 1.9 has no normalized field for it.

A permission-mode change maps to Authorize Session with the `Assign
Privileges` activity and the new mode in `privileges` against the agent's
session. Device Config State Change cannot carry the AI Operation profile, so
it cannot name the agent that changed the setting. The previous mode and the
trigger stay in `unmapped`, and the message says who changed it: a keypress
or command is the person, while `auto_gate_denied` is the harness demoting
the session on its own after its automatic gate refused a call. The record
reports a change that happened, so its status is Success. Severity follows
the autonomy the new mode grants: `bypassPermissions` is `Medium`, `auto`,
which lets a classifier approve on the agent's behalf, is `Low`, and modes
that ask a person or only plan are `Informational`. Codex reports its
approval and sandbox policy only at conversation start and emits nothing
when a person changes them during a session, so no Codex counterpart exists.

A decision on a local tool that has no OCSF class, such as `Skill`, `Agent`,
`CronCreate`, or a file tool whose decision reports no path, falls back to
Base Event but keeps the Security Control profile: a person rejecting a
`Skill` call is the same supervised-versus-autonomous signal as on any other
class. Base Event cannot carry the AI Operation profile or an actor, so the
session and the tool name stay in `unmapped` there rather than surviving only
in `raw_data`, and `message` names the tool and the outcome.

A skill activation maps to Application Lifecycle with the `Enable` activity,
and the skill document is the agent's charter in `ai_agent.charter`. A plugin
load is the same lifecycle verb, `Enable`. The telemetry reports no hash of
the skill or plugin content it loads, so charter integrity is not attestable;
that is a vendor gap, not a mapping choice.

With `include_content=true`, the text of a user prompt or assistant response
lands in `message_context.prompt_text` and `response_text`, the fields OCSF
1.9 added for conversation text. The SHA-256 hash stays in
`unmapped.content_hash` as the integrity handle, which has no schema home
yet. Each conversation turn stays its own API Activity event because the
agent emits it as a discrete record; folding it into the model call would
need a stateful cross-event join.

API Activity is a local fallback for conversation turns, not a claim that the
audit transport is the activity. OCSF 1.9 has no concrete prompt activity class
that can carry the AI Operation profile without introducing unrelated required
fields. The session stays in `message_context.uid`; a reported `prompt.id`
stays temporarily in `message_context.name` and `unmapped` because OCSF has no
dedicated turn identifier.

The serving MCP server lands in `api.service.name` and
`dst_endpoint.svc_name` on every MCP event, derived from the
`mcp__<server>__<tool>` tool-name convention or from Claude Code's
`tool_parameters`. The latter reports MCP calls as the generic `mcp_tool`, so
the mapper extracts `mcp_server_name` and `mcp_tool_name` to retain the actual
service and operation. With `include_content=true`, parsed tool input lands in
`api.request.data`. MCP resource reads and web fetches also identify their URI
as a target in `resources`.

Discrete tool-result logs retain their runtime as `unmapped.duration_ms`.
Top-level OCSF `duration` is reserved for aggregate windows. Spans that are
mapped use the Trace profile with the provider's real start time, end time,
and `trace.span.duration`.

Fields deprecated in OCSF 1.9.0 are not used. The acting application is
`actor.application.name` rather than `actor.app_name`, and a skill or plugin
lifecycle event names its subject in `application` rather than `app`. Because
`application` carries no `vendor_name` of its own, a plugin's marketplace lands
in `application.product.vendor_name`.

`device.type_id` is required, so it is now set on every event that carries a
device, including the ones that report a hostname. Its value is `0` (Unknown)
throughout: the telemetry never says whether the host is a laptop, a server or
a VM, and guessing would be worse than saying so.

The source of an authorization decision fills `policy.type` in both places it
appears, on the top-level `policy` and on `authorizations[].policy`. It
names the kind of control that decided rather than a named rule, and
`policy.name` stays empty because inventing a rule identity would make a
category look like a specific rule.

The `device` object is attached only when the resource names the host. OCSF
constrains `device` to at least one identifying attribute, so a device built
from `type_id` alone is not a valid object, and inventing a host the source
never reported would be worse than leaving the required field empty. Events
without a host therefore carry no `device` at all.
