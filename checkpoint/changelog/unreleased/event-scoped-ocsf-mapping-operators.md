---
title: OCSF 1.9 normalization contract
type: breaking
authors:
  - mavam
  - codex
created: 2026-06-13T07:58:15.702248Z
---

Use `checkpoint::ocsf::normalize` to normalize structured Check Point events to OCSF 1.9:

```tql
checkpoint::ocsf::normalize
```

The lower-level `checkpoint::ocsf::map` operator remains available for pipelines that need
separate structured source and OCSF output fields.
