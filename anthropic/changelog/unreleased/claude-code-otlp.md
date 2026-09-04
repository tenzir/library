---
title: Normalize Claude Code OTLP telemetry
type: feature
authors:
  - philip
components:
  - anthropic
created: 2026-07-29T00:00:00Z
---

The Anthropic package now normalizes Claude Code OTLP logs and traces and maps
them directly to OCSF 1.9.0. Agent-mediated activity uses the AI Operation
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
commands, and file operations. Potentially sensitive prompt, response, command,
and tool content is hashed unless `include_content=true` is explicitly set.
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

The OCSF mapping names the API activity only when the operation states it: an
HTTP verb, or an event kind such as a model completion or connection setup.
Tool names and MCP method paths get `Other` with the operation in
`activity_name`, as the schema prescribes when no enum member fits; guessing
read/write intent from the shape of a name would misclassify a tool such as
`cleanup_stale_records` as a read. `metadata.original_event_uid` prefers
identifiers that are
unique per event, because `span_id` identifies the enclosing span and is shared
by every record emitted inside it; the span itself is preserved as described
below. A denied tool call is rated `Low` instead of
`Informational`. Normalization artifacts no longer leak into `unmapped`:
`signal` and `transport` are internal, and `decision_source` lands in the
Security Control `policy` and in `actor.authorizations[].policy.name`.
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
share it, so it stays on `script.uid`, `process.uid` and `api.request.uid`, and
in `unmapped` on classes with no typed home for it.

`metadata.correlation_uid` always identifies the trace, so grouping by it never
mixes a single transaction with a whole session. Events whose source carries no
trace leave it empty; the session is available as `ai_agent.instance_uid`, and
on classes with an actor also as `actor.session.uid`.

Shell commands map to Script Activity: what the tool span attests is a command
string, not a process, so the call reports `Execute` with the command in
`script.script_content` and its SHA-256 digest in `script.hashes`. The result
log keeps Process Activity semantics: a foreground completion reports
`Terminate`, and a backgrounded command, which is still running when its
result arrives, reports `Launch`.

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
policy block. Tool decisions no longer place the provisioning source
(`tool_source`) into `api.service.name`, which other producers use for the
MCP server name; the tool name stays in `api.operation` until the proposed
OCSF `ai_tool` object provides a home for tool identity.

A permission-mode change maps to Authorize Session with the `Assign
Privileges` activity and the new mode in `privileges` against the agent's
session. Device Config State Change cannot carry the AI Operation profile, so
it cannot name the agent that changed the setting. Switching to
`bypassPermissions` is rated `Medium`.

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

The serving MCP server lands in `dst_endpoint.svc_name` on every MCP event,
derived from the `mcp__<server>__<tool>` tool-name convention, matching the
placement that connection events already use. This is the package's declared
placement until the proposed `ai_tool` object gives the serving system a
schema home.

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
appears, on the top-level `policy` and on `actor.authorizations[].policy`. It
names the kind of control that decided rather than a named rule, and
`policy.name` stays empty because inventing a rule identity would make a
category look like a specific rule.

The `device` object is attached only when the resource names the host. OCSF
constrains `device` to at least one identifying attribute, so a device built
from `type_id` alone is not a valid object, and inventing a host the source
never reported would be worse than leaving the required field empty. Events
without a host therefore carry no `device` at all.
