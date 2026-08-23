---
title: OCSF 1.9 normalization contract
type: breaking
authors:
  - mavam
  - codex
created: 2026-06-13T07:58:21.799017Z
---

Use `zeek::ocsf::normalize` to normalize structured Zeek events to OCSF 1.9:

```tql
zeek::ocsf::normalize
```

The lower-level `zeek::ocsf::map` operator remains available for pipelines that need
separate structured source and OCSF output fields.
