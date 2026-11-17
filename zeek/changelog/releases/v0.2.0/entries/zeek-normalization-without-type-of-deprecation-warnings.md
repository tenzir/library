---
title: Zeek normalization without `type_of` deprecation warnings
type: bugfix
authors:
  - IyeOnline
prs:
  - 200
created: 2026-10-20T00:00:00Z
---

The Zeek OCSF mapping no longer emits `type_of` deprecation warnings on Tenzir v6.20. It now detects time and floating-point `ts` values with the `type_kind` function, and still maps both to the OCSF `time` field.

Native connection durations, DHCP lease durations, DNS TTLs, and unsigned response codes are also normalized without conversion warnings.
