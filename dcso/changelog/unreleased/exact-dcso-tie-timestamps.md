---
title: Exact DCSO TIE timestamps
type: bugfix
authors:
  - zedoraps
created: 2026-11-21T13:44:05.263429Z
---

Timestamps are rounded to the microseconds that DCSO TIE writes, so `2026-11-02T18:13:18.328751` no longer becomes `2026-11-02T18:13:18.328750999` on some Tenzir versions.
