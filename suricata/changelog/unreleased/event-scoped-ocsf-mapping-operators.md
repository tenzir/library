---
title: OCSF 1.9 normalization contract
type: breaking
authors:
  - mavam
  - codex
created: 2026-06-13T07:58:21.077264Z
---

Use `suricata::ocsf::normalize` to normalize structured Suricata EVE events to OCSF 1.9:

```tql
suricata::ocsf::normalize
```

The lower-level `suricata::ocsf::map` operator remains available for pipelines that need
separate structured source and OCSF output fields.
