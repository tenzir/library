---
title: Parameter names for unnamed Windows event data
type: change
authors:
  - zedoraps
created: 2026-11-20T08:29:21.798384Z
---

Unnamed event data from legacy providers, such as Application Error, now uses the names `param1`, `param2`, … for all collectors.

| Collector | Before | Now |
|---|---|---|
| Windows Event XML | `unmapped.EventData._0`, `_1`, … | `param1`, `param2`, … |
| Winlogbeat | `param1`, `param2`, … | Unchanged |

**What you need to do:** Replace `unmapped.EventData._0` with `unmapped.EventData.param1`, and shift every other index by one.

**Why:** The names match Winlogbeat and the `%1`, `%2` inserts of the provider's message.
