---
title: Zeek normalization without `type_of` deprecation warnings
type: bugfix
authors:
  - IyeOnline
prs:
  - 200
created: 2026-10-20T00:00:00Z
---

The Zeek OCSF mapping no longer emits `type_of` deprecation warnings on Tenzir v6.20. It now detects time and floating-point `ts` values with the `is_time_type` and `is_float_type` functions, and still maps both to the OCSF `time` field.
