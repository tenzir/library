---
title: Event-scoped OCSF mapping operators
type: breaking
authors:
  - mavam
  - codex
created: 2026-06-13T07:58:00.996294Z
---

Amazon OCSF mapping operators take the structured source and OCSF output
fields positionally.

```tql
amazon::vpc_flow::ocsf::map vpc_flow, ocsf
amazon::route53::ocsf::map route53, ocsf
```

The VPC Flow Log package also provides `amazon::vpc_flow::ocsf::normalize` for
turning a supported raw line into OCSF with `raw_data` provenance.
