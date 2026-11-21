---
title: Windows event times without rounding errors
type: bugfix
authors:
  - zedoraps
created: 2026-11-21T11:50:05.705037Z
---

Windows event times are rounded to the 100-nanosecond precision that Windows records, so every Tenzir version yields the same value, such as `2024-12-30T09:18:50.491909Z` instead of `2024-12-30T09:18:50.491908999Z`.
