---
title: Exact Suricata timestamps
type: bugfix
authors:
  - zedoraps
created: 2026-11-21T14:35:23.757799Z
---

Timestamps are rounded to the microseconds that Suricata EVE writes, so a time such as `18:22:26.927489` no longer becomes `18:22:26.927488999` on some Tenzir versions.
