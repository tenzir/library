# Agent demo captures

The Claude Code and Codex sources replay recordings with invented content. The
files hold one OTel log record or span per line, as `accept_otlp` with
`schema="record"` emits it, compressed with Zstandard. They contain native
telemetry, not previously mapped OCSF events.

## Replay a local recording

```tql
from_file "claude-code.ndjson" {
  read_lines
}
raw = move line
demo::agents::replay
anthropic::claude_code::ocsf::normalize include_content=true
```

For Codex, use `codex.ndjson` and `openai::codex::ocsf::normalize`. The replay
operator moves the telemetry timestamps to the current time and restores the
schema name and the types. Recorded durations, the order of events, and dates
inside prompts, commands, and outputs stay unchanged. Use `demo::agents::parse` to
parse a record without a replay. See [REPLAY.md](REPLAY.md) for the common
arguments.

`demo::claude_code` and `demo::codex` download the public
[Claude Code](https://datasets.tenzir.tools/demo/v1/claude-code/otel.ndjson.zst) and
[Codex](https://datasets.tenzir.tools/demo/v1/codex/otel.ndjson.zst) datasets once, when
the pipeline starts. These sources average about one event per second.

Each cycle renews the correlation IDs. Tool, request, session, conversation,
message, trace, and span references remain linked within that cycle, including
references inside tool arguments and outputs. Fixed prefixes such as `toolu_`,
`call_`, `req_`, and `exec-` remain intact. UUIDs keep their layout, and trace
and span IDs remain 32 and 16 hexadecimal characters. User, organization, and
host identities stay stable. Missing IDs stay missing.

## Capture selection

The corpus contains a full hour of meaningful logs, supplemented by
short excerpts for less common activity. Metrics and high-volume streaming
transport notifications are excluded. Frequencies therefore describe the
selected activity logs, not all OpenTelemetry traffic.

| Selection | Raw records | Purpose |
| --- | ---: | --- |
| Baseline hour | 1,990 | Common prompt, model, tool, process, and file activity |
| Permission excerpt | 234 | Permission changes and surrounding activity |
| Refusal excerpt | 21 | A refusal and surrounding activity |
| Codex web/MCP excerpts | 6 | Search, resource access, and a failed remote fetch |

The dataset places these excerpts on a fixed demo timeline in their original
chronological order.

This is broad coverage, not an exhaustive list of supported tools. The extracts
include process exit failures, polling, patch additions, updates, and deletions.
Some tool results have no matching decision in the selected data. Missing
events are not synthesized. The three supporting spans in the web/MCP excerpts
do not produce additional OCSF events in the current Codex normalizer.

## Content handling

The recordings come from real sessions, but their content is invented. Prompts,
responses, tool inputs, arguments, outputs, patches, commands, paths, hosts,
repositories, and dates belong to a made-up project, `example-org/inventory-service`.
Encrypted messages between agents are random bytes. All identifiers are random,
keep the layout of the product, and stay consistent within a recording, also
inside content.

Event types, tool names, decisions, models, outcomes, durations, token counts,
costs, and payload sizes are the recorded ones. They describe the original
sessions, not the invented content. Pauses longer than 5 seconds were shortened,
so a duration can exceed the time since the previous record. The recordings are
not claimed to be anonymous.
