---
title: OCSF 1.9 mapping contract
type: breaking
authors:
  - mavam
  - codex
created: 2026-06-13T07:58:23.2253Z
---

`fortinet::fortigate::ocsf::map` now takes an optional positional source field
and a named `into` output. Both default to `this`. The mapper does not choose
raw provenance.

```tql
fortinet::fortigate::ocsf::map fortinet, into=ocsf
ocsf.raw_data = move line
ocsf.raw_data_size = ocsf.raw_data.length_bytes()
this = ocsf
```
