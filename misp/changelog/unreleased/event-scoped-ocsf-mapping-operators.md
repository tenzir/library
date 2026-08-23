---
title: OCSF 1.9 normalization contract
type: breaking
authors:
  - mavam
  - codex
created: 2026-06-13T07:58:18.719629Z
---

Use `misp::event::ocsf::normalize` to normalize structured MISP events to OCSF 1.9:

```tql
misp::event::ocsf::normalize
```

The lower-level `misp::event::ocsf::map` operator remains available for pipelines that need
separate structured source and OCSF output fields.
