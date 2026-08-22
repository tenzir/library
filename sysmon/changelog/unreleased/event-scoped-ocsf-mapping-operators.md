---
title: Event-scoped OCSF mapping operators
type: breaking
authors:
  - mavam
  - codex
created: 2026-06-13T07:58:23.948112Z
---

The Sysmon OCSF mapper takes the structured source and OCSF output fields positionally. Preserve raw log data by parsing first, mapping the parsed event, and assigning `raw_data` and `raw_data_size` after mapping.

Before:

```tql
pkg::ocsf::map source
```

After:

```tql
pkg::ocsf::map event=source
source.raw_data = move raw
source.raw_data_size = source.raw_data.length_bytes()
this = source
```
