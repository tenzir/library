---
title: OCSF 1.9 normalization contract
type: breaking
authors:
  - mavam
  - codex
created: 2026-06-13T07:58:23.948112Z
---

Use `sysmon::ocsf::normalize` to normalize structured Microsoft Sysmon events to OCSF 1.9:

```tql
sysmon::ocsf::normalize
```

The lower-level `sysmon::ocsf::map` operator remains available for pipelines that need
separate structured source and OCSF output fields.
