The new Agentmetry package maps the tool calls, approvals, and detections that Agentmetry records for AI coding agents to OCSF 1.9.0. Tool calls from Claude Code also carry the harness's tool-use ID and its reported status and duration, and detection findings show the tool calls that triggered them as evidence.

## 🚀 Features

### Agentmetry package for OCSF

The library now includes an `agentmetry` package that maps events from [Agentmetry](https://github.com/blitzcrieg1/agentmetry), the open-source recorder for AI coding agents, to OCSF 1.9.0.

Agentmetry records the tool calls of Claude Code, Cursor, Codex, GitHub Copilot, and several more agents from their own hooks. It writes one JSON object per event, either to a hash-chained trail or through its webhook sink, which Tenzir reads natively, so you only need the normalizer:

```tql
from_file "agentmetry-trail.jsonl" {
  read_ndjson
}
agentmetry::ocsf::normalize
```

| Agentmetry events                                                       | OCSF class           |
| ----------------------------------------------------------------------- | -------------------- |
| `tool_called`, `approval_request`, `approval_response` for a shell tool | Process Activity     |
| the same for a file tool, when the event names the file                 | File System Activity |
| the same for any other tool, including MCP tools                        | API Activity         |
| `detection`, `mcp_schema` with outcome `changed`                        | Detection Finding    |

Tool calls get the AI Operation profile, with the agent and its session in `ai_agent`. A call that a policy denied, and a person's decision on an approval request, get the Security Control profile. A detection keeps its severity, its ATT&CK identifiers, and the calls it matched.

*By @blitzcrieg1 in #211.*

### Evidence from the tool calls behind Agentmetry detections

Agentmetry detection findings now show the tool calls that triggered them as OCSF evidence. Each call appears with its event ID and tool name, plus the file path or URL when Agentmetry captured one, so you can see what the agent touched without looking up the original events.

*By @blitzcrieg1 in #227.*

### Reported results and invocation IDs for Agentmetry tool calls

Agentmetry tool calls from Claude Code now carry what the harness reported about each call. The tool-use ID that links a request to its result becomes `process.uid` of a shell call and `api.request.uid` of an API call, so a shell call from Claude Code no longer triggers the OCSF warning about a process without identity. A result's reported status becomes `status_code` and its reported execution time becomes `duration`, including a duration of zero. Neither proves that the tool ran or how it ended, so the outcome still decides `status_id`.

*By @blitzcrieg1 and @mavam in #229.*

## 🐞 Bug fixes

### Map Agentmetry shell calls from recorded tool names

Agentmetry records the shell calls of Codex and Cursor under server `shell`, for example as tool `run`, and those of Antigravity as `run_command`. These now map to Process Activity instead of API Activity, including inferred approval responses. A tool named `run` on another server stays API Activity.

*By @blitzcrieg1 in #225.*

### OCSF context handling for Agentmetry

Agentmetry normalization now sets `device.type_id` to Unknown for reported hosts and creates optional actor, analytic, and endpoint objects only when the source identifies them. Actor details without an ID remain under their original keys in `unmapped`.

*By @zedoraps in #225.*

### Preserve inferred Agentmetry approval outcomes

An Agentmetry approval response inferred from a subsequent tool call now keeps its reason and maps to Unknown disposition. A session that ends with a pending request also keeps its inferred reason and Unknown disposition. Qualified built-in shell tool names such as `codex.exec_command` map to Process Activity.

*By @blitzcrieg1 in #222.*

### Source timestamps for Agentmetry fallback events

Agentmetry normalization now maps `timestamp_utc` to the OCSF event time even when the record has no action type and becomes a Base Event. Records without a timestamp still have no event time; the mapping does not invent one.

*By @mavam in #225.*

### Valid OCSF evidence for Agentmetry detections

Agentmetry detection evidence now includes the identified acting user alongside the AI agent, satisfying OCSF 1.9's evidence constraint. When no acting user is identified, the agent remains under `unmapped.agent` rather than producing invalid evidence. Actor-only detections also retain their evidence.

*By @mavam in #225.*
