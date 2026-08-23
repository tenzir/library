---
title: OCSF 1.9 normalization contract
type: breaking
authors:
  - mavam
  - codex
created: 2026-06-13T07:58:17.982827Z
---

Use `foxio::ocsf::normalize` to normalize structured FoxIO JA4+ records to
OCSF 1.9:

```tql
foxio::ocsf::normalize
```

The lower-level `foxio::ocsf::map` operator remains available for pipelines
that need separate structured source and OCSF output fields.
