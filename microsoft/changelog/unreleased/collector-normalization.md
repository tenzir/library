---
title: Collector normalization
type: feature
authors:
  - mavam
prs:
  - 180
created: 2026-08-27T06:33:48.406501Z
---

Normalize structured Windows Event Log events from Fluent Bit, NXLog, and Winlogbeat without collector-specific OCSF mappings. This includes Sysmon, Security, PowerShell, Defender, and other providers:

```tql
from_file "windows-events.nxlog.ndjson" {
  read_ndjson unflatten_separator="."
}
microsoft::windows::ocsf::normalize
metadata.log_format = "json"
```

Configure Fluent Bit with `event_data_as_map true` and `string_inserts false` to preserve named provider fields without positional duplicates. Configure NXLog with `AddPrefix TRUE` so provider fields remain distinct from collector metadata. Winlogbeat events use the structured `winlog` object and retain the remaining ECS fields under `unmapped.Winlogbeat`. The normalizer also accepts Windows Event Log XML directly. For staged processing, use `microsoft::windows::canonicalize` to produce the canonical Windows Event Log structure, then pass the result to `microsoft::windows::ocsf::map`. Add `metadata.log_format`, `raw_data`, and `raw_data_size` in the calling pipeline, where the source format and payload are known.
