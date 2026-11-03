---
title: Agentmetry package for OCSF
type: feature
authors:
  - blitzcrieg1
prs:
  - 211
  - 208
created: 2026-11-02T20:00:00.000000Z
---

The library now includes an `agentmetry` package that maps events from [Agentmetry](https://github.com/blitzcrieg1/agentmetry), the open-source recorder for AI coding agents, to OCSF 1.9.0.

Agentmetry records the tool calls of Claude Code, Cursor, Codex, GitHub Copilot, and several more agents from their own hooks. It writes one JSON object per event, either to a hash-chained trail or through its webhook sink, which Tenzir reads natively, so you only need the normalizer:

```tql
from_file "agentmetry-trail.jsonl" {
  read_ndjson
}
agentmetry::ocsf::normalize
```

| Agentmetry events | OCSF class |
|---|---|
| `tool_called`, `approval_request`, `approval_response` for a shell tool | Process Activity |
| the same for a file tool, when the event names the file | File System Activity |
| the same for any other tool, including MCP tools | API Activity |
| `detection`, `mcp_schema` with outcome `changed` | Detection Finding |

Tool calls get the AI Operation profile, with the agent and its session in `ai_agent`. A call that a policy denied, and a person's decision on an approval request, get the Security Control profile. A detection keeps its severity, its ATT&CK identifiers, and the calls it matched.

Reported hosts use `device.type_id = 0` (Unknown) because Agentmetry does not report the device type. Events without a reported host leave `device` unset and retain their event class so validation can report missing required context.
