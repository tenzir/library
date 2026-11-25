---
title: Unset times in Zeek NTP events
type: bugfix
authors:
  - zedoraps
prs:
  - 268
created: 2026-11-25T00:00:00Z
---

`demo::zeek` keeps unset NTP times at 1970-01-01T00:00:00Z instead of moving them by hours.
