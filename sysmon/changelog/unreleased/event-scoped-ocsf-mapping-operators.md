---
title: Event-scoped OCSF mapping operators
type: breaking
authors:
  - mavam
  - codex
created: 2026-06-13T07:58:23.948112Z
---

OCSF mapping operators now take a named `event` field argument that defaults to `this` and perform all mapping work inside that explicit event scope. Preserve raw log data by parsing first, mapping the parsed event, and assigning `raw_data` and `raw_data_size` after mapping.

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
