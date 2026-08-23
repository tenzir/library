---
title: OCSF 1.9 normalization contracts
type: breaking
authors:
  - mavam
  - codex
created: 2026-06-13T07:58:00.996294Z
---

Use the source-specific `normalize` operators to turn VPC Flow Log lines or
structured Route 53 Resolver Query Log events into OCSF 1.9:

```tql
amazon::vpc_flow::ocsf::normalize
amazon::route53::ocsf::normalize
```
