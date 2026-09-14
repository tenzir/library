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
demo::agents::replay start=now()
anthropic::claude_code::ocsf::normalize include_content=true
```

For Codex, use `codex.json` and `openai::codex::ocsf::normalize`.
The parser restores each record's native schema from its `schema` and `event`
envelope. The replay operator moves the capture to the current time and divides
event gaps by `speed`. Collector delay and recorded durations stay unchanged.
Add `pace=true` to wait between events. Without pacing, it emits the capture
immediately.

`demo::claude_code` and `demo::codex` download the public
[Claude Code](https://datasets.tenzir.tools/claude-code/otel.json.zst) and
[Codex](https://datasets.tenzir.tools/codex/otel.json.zst) datasets.
No local files or volume mounts are required.
No arguments are required. These sources average about one event per second,
retaining the original bursts and pauses at a compressed timescale.
That is roughly 600 events per 10 minutes over repeated playback, not a quota
for every 10-minute window. `speed=2.0` doubles the average rate. Like OpenSSH,
they compress each capture to its replay period and pace the resulting timestamps.

The cycle periods are `469s / speed` for Claude Code and `1782s / speed` for
Codex, matching their capture sizes. Loading and rotating IDs adds startup time
to each cycle. Recorded durations stay unchanged; the demo timeline does not
represent the original time between related events.

Each cycle rotates correlation IDs with a fresh seed. Tool, request, session,
conversation, message, trace, and span references remain linked within that
cycle, including references inside tool arguments and outputs. Fixed prefixes
such as `toolu_`, `call_`, `req_`, and `exec-` remain intact. UUIDs keep their
layout, and trace and span IDs remain 32 and 16 hexadecimal characters.
Anonymized user and host identities stay stable. Missing IDs stay missing.

For a finite local replay with fresh IDs, insert
`demo::agents::rotate_ids seed=uuid()` before `demo::agents::replay`.
ID rotation buffers one capture to resolve references across its records.

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
