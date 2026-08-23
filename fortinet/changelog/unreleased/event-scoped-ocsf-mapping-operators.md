---
title: OCSF 1.9 normalization contract
type: breaking
authors:
  - mavam
  - codex
created: 2026-06-13T07:58:23.2253Z
---

Use `fortinet::fortigate::ocsf::normalize` to normalize structured FortiGate
events to OCSF 1.9:

```tql
fortinet::fortigate::ocsf::normalize
```

The lower-level `fortinet::fortigate::ocsf::map` operator remains available for
pipelines that need separate structured source and OCSF output fields.
