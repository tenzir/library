---
title: OCSF 1.9 normalization contract
type: breaking
authors:
  - mavam
  - codex
created: 2026-06-13T07:58:20.370947Z
---

Use `sophos::ocsf::normalize` to normalize structured Sophos Central events to OCSF 1.9:

```tql
sophos::ocsf::normalize
```

The lower-level `sophos::ocsf::map` operator remains available for pipelines that need
separate structured source and OCSF output fields.
