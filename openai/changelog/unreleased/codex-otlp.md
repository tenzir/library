---
title: Normalize Codex OTLP telemetry
type: feature
authors:
  - zedoraps
components:
  - openai
created: 2026-07-29T00:00:00Z
---

The OpenAI package normalizes security-relevant Codex OTLP telemetry to OCSF
1.9.0, including process and file activity, remote calls, conversation records,
JSON-RPC operations, HTTP activity, authorization, and skill activation.

```tql
accept_otlp "0.0.0.0:4318", transport="http", schema="record"
where @name in ["otel.log", "otel.span"]
openai::codex::ocsf::normalize
ocsf_derive
ocsf_cast
```

Shell decisions and confirmed completions use Process Activity Launch and
Terminate with a shared call-derived UID. The mapper reads command exit codes
from `exec_command` result envelopes instead of treating tool success as process
success. Running or unrecognized results use Observe with Unknown status.
Argument-validation failures remain Base Events, not process launches.
Records emit independently; `write_stdin` remains a separate tool interaction.

Shell command text is always retained, but process creation time and PID are
not inferred. File patches produce one event per affected file. Explicit Add
File operations map to Create and generic Write to Update. Deletion flags and
rename results describe successful, non-denied changes only.

Remote authorization and invocation use API Activity Authorize and Invoke.
MCP service, operation, call ID, and resource URI retain their separate
destinations, including separately reported tool namespaces. MCP hook spans
with explicit server and tool identities map to Invoke with actual trace timing.
Unknown local activity remains Base Event.

Conversation records use API Activity Prompt, Respond, and Turn. JSON-RPC
operations use Call. HTTP records with a method and server address use HTTP
Activity. Internal runtime spans and duplicate tool spans are filtered.

Trace IDs and log span IDs survive normalization. Logs retain span context
without inventing a span lifetime; complete mapped spans retain their timing.
Missing parent IDs, status messages, and log attributes are handled without
warnings.

The package contains operators and receiver examples, without packaged pipelines.
A thin `ocsf::normalize` wrapper preserves raw input around the canonicalizer
and field-based mapper. Shared context and event-specific operators keep the
mapping dispatcher small.

The default `include_content=false` omits copied content from normalized fields;
it does not redact `raw_data` or shell commands. Review storage access and
retention accordingly. Input is native OTLP records only; no shared OTEL
package or legacy-envelope operators are required or included.

See the package README for the mapping tables, identifiers, filtering rules,
and configuration.
