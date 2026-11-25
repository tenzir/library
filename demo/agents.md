# Agent demo captures

The Claude Code and Codex sources replay anonymized captures from the log lab.
The source files contain readable JSON records compressed with Zstandard, like
the OpenSSH dataset. They contain native telemetry, not previously mapped OCSF
events.

## Replay a local capture

```tql
from_file "claude-code.json" {
  demo::agents::read
}
demo::agents::replay
anthropic::claude_code::ocsf::normalize include_content=true
```

For Codex, use `codex.json` and `openai::codex::ocsf::normalize`.
The parser restores each record's native schema from its `schema` and `event`
envelope. The replay operator moves the telemetry timestamps to the current
time. Recorded durations, the order of events, and dates inside prompts,
commands, and outputs stay unchanged. Pauses longer than `max_gap`, by default
5 s, are cut. See [REPLAY.md](REPLAY.md) for the common arguments.

`demo::claude_code` and `demo::codex` download the public
[Claude Code](https://datasets.tenzir.tools/claude-code/otel.json.zst) and
[Codex](https://datasets.tenzir.tools/codex/otel.json.zst) datasets once, when
the pipeline starts. These sources average about one event per second.

Each cycle renews the correlation IDs. Tool, request, session, conversation,
message, trace, and span references remain linked within that cycle, including
references inside tool arguments and outputs. Fixed prefixes such as `toolu_`,
`call_`, `req_`, and `exec-` remain intact. UUIDs keep their layout, and trace
and span IDs remain 32 and 16 hexadecimal characters. Anonymized user,
organization, and host identities stay stable. Missing IDs stay missing.

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
chronological order. It removes the long gaps between captures, but preserves
timing within each excerpt. The `scenario` field identifies each excerpt; the
parser removes this dataset metadata before normalization.

This is broad coverage, not an exhaustive list of supported tools. The extracts
include process exit failures, polling, patch additions, updates, and deletions.
Some tool results have no matching decision in the selected data. Missing
events are not synthesized. The three supporting spans in the web/MCP excerpts
do not produce additional OCSF events in the current Codex normalizer.

## Content handling

Prompts and identifying response text are rewritten for the demo. Related commands, paths,
identities, and outputs must use the same replacements. Of the 15 Claude prompt
records, 13 contain rewritten text and two remain metadata-only. The Codex
capture contains 98 rewritten prompt records. Prompt and response lengths
describe the replacement text. Recorded token usage and tool payload-size
counters describe the original interaction, not the replacement text.

The raw exports and private replacement manifest stay outside this repository.
Do not publish a candidate dataset until the rewritten records have passed a
privacy review and normalization checks.
