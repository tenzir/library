---
title: Normalize Claude Code OTLP telemetry
type: feature
authors:
  - philip
components:
  - anthropic
created: 2026-07-29T00:00:00Z
---

The Anthropic package normalizes Claude Code OTLP telemetry to OCSF 1.9.0,
including process and file activity, remote tool calls, conversation records,
authorization, authentication, and application lifecycle events.

```tql
subscribe "otlp"
where @name in ["otel.log", "otel.span"]
anthropic::claude_code::ocsf
ocsf_derive
ocsf_cast
```

Shell decisions and foreground results use Process Activity Launch and
Terminate with a shared tool-call-derived UID. Background results use Observe
with Unknown status, without claiming that a process is still running.
Records emit independently; no correlation window delays them. Shell command
text is always retained, but process creation time and PID are not inferred.

File mappings distinguish filename search from content reads. Glob maps to
Search and Grep to Read when a target is reported, without assuming the target
is a folder. Generic Write maps to Update. Deletion flags, rename results, and
edit diffs describe successful, non-denied changes only.

Remote authorization and invocation use API Activity Authorize and Invoke.
MCP service, operation, call ID, and resource URI retain their separate
destinations. Prompts and responses use API Activity Prompt and Respond with
conversation text in `message_context` when content is enabled. Unknown local
activity remains Base Event.

Login maps to Authentication / Logon, plugin installation to Application
Lifecycle / Install, and retry exhaustion to Application Error / General Error.
Retry counts and timing remain available without creating another model call.

Trace IDs and log span IDs survive normalization. Logs retain span context
without inventing a span lifetime; complete mapped spans retain their timing.
Missing optional span fields no longer produce warnings.

The optional ClickHouse pipeline retains Base Events alongside specific
classes, excludes metrics, and stores queryable nested JSON in event.
Its application column uses `actor.application.name`. Other pipeline paths
can retain selected native metrics.

The default `include_content=false` omits copied content from normalized fields;
it does not redact `raw_data` or shell commands. Review storage access and
retention accordingly. Input is native OTLP records only; no shared OTEL
package or legacy-envelope operators are required or included.

See the package README for the mapping tables, identifiers, filtering rules,
and configuration.
