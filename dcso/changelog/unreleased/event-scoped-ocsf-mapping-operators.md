---
title: OCSF 1.9 normalization contract
type: breaking
authors:
  - mavam
  - codex
created: 2026-06-13T07:58:17.167216Z
---

Use `dcso::tie::ocsf::normalize` to normalize structured DCSO TIE events to OCSF 1.9:

```tql
dcso::tie::ocsf::normalize
```

The lower-level `dcso::tie::ocsf::map` operator remains available for pipelines that need
separate structured source and OCSF output fields.
