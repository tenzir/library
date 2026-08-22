---
title: OCSF 1.9 mapping contract
type: breaking
authors:
  - mavam
  - codex
created: 2026-06-13T07:58:23.2253Z
---

`fortinet::fortigate::ocsf::map` takes the structured source and OCSF output
fields positionally. The mapper does not choose raw provenance.

```tql
fortinet::fortigate::ocsf::map fortinet, ocsf
ocsf.raw_data = move line
ocsf.raw_data_size = ocsf.raw_data.length_bytes()
this = ocsf
```
