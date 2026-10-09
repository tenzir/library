---
title: Event time for floating-point timestamps on Tenzir v6.20
type: bugfix
authors:
  - IyeOnline
  - claude
created: 2026-10-09T12:00:00Z
---

The OCSF mapping now sets `time` from a floating-point `ts` field on Tenzir
v6.20 and later. Previously, such events kept `ts` in `unmapped` and had no
`time`, because Tenzir v6.20 reports the type of these values as `float`
instead of `double`.
