This release replays Zeek, Suricata, OpenSSH, Windows, Claude Code, and Codex recordings as endless live feeds with current timestamps and new identifiers in every cycle. Replacing a feed with your own source turns an example into a working pipeline.

## 💥 Breaking changes

### Seamless demo replay

All demo feeds now replay without gaps, with current timestamps, and with new identifiers in every cycle:

- All feeds begin with the first event of their recording, share the arguments `speed` and `cycles`, and download the recording once.
- All feeds emit what the collector or reader emits: `demo::windows` the raw `line` instead of `time`, `format`, and `raw`, and the agent feeds `event.timestamp` as a string.
- `demo::zeek` and `demo::suricata` replay the same 20 minutes of an invented office with a small incident.
- `demo::replay::run`, `demo::replay::events`, and `demo::replay::renew_ids` replay your own short recordings.
- Every feed has a plain example and one that normalizes to OCSF, which names the package it requires. The examples no longer publish to a topic.
- `demo::agents::read`, `demo::agents::rotate_ids`, and `demo::agents::shift_time` are gone. Use `demo::agents::replay` instead, which expects OTel records in JSON.

*By @zedoraps in #267.*

### Standalone demo sources

The demo package now provides Suricata and Zeek demo sources as reusable operators and examples instead of installing configured pipelines.

Use the examples as starting points and pass source speed directly where you run the demo workflow. Installing the package no longer starts demo data generation through package inputs.

*By @mavam and @codex in #147.*

## 🚀 Features

### Claude Code and Codex demo sources

The new `demo::claude_code` and `demo::codex` operators continuously replay public agent telemetry with invented content, without a local dataset or a live agent:

```tql
demo::claude_code
anthropic::claude_code::ocsf::normalize include_content=true
```

Use `demo::codex` with `openai::codex::ocsf::normalize` for Codex. Each source averages about one event per second by default while retaining bursts and pauses. Set `speed=2.0` to double that rate. Each replay cycle uses current timestamps and fresh correlation IDs, preserving related references and fixed ID prefixes.

*By @zedoraps in #187.*

### OpenSSH Syslog demo source

The new `demo::openssh` operator replays OpenSSH `sshd` Syslog captures from six Linux distributions in real time. Pair it with the `openssh` package to demonstrate parsing, correlation, and OCSF mapping without a live SSH server:

```tql
demo::openssh
where app_name in openssh::$app_names
openssh::ocsf::normalize
```

*By @zedoraps in #178.*

### Windows event demo source

The new `demo::windows` operator replays raw Windows events captured in a test lab as Winlogbeat NDJSON, Fluent Bit NDJSON, or Windows Event Log XML. Pair it with the `microsoft` package to demonstrate collector-independent normalization to OCSF:

```tql
demo::windows "winlogbeat"
event = line.parse_json()
microsoft::windows::ocsf::normalize event, into=ocsf
this = move ocsf
```

*By @zedoraps.*
