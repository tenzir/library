---
title: Event-scoped OCSF mapping operators
type: breaking
authors:
  - mavam
  - codex
created: 2026-06-13T07:58:22.47847Z
---

The Zscaler OCSF mapper takes the structured source and OCSF output fields positionally.

Before:

```tql
pkg::ocsf::map source
```

After:

```tql
pkg::ocsf::map event=source
```
