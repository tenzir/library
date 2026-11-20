---
title: Parameter names for unnamed Windows event data
type: change
authors:
  - zedoraps
created: 2026-11-20T08:29:21.798384Z
---

Unnamed event data now uses the names `param1`, `param2`, and so on, for all collectors. Legacy providers, such as Application Error and Windows Error Reporting, write event data without field names. Windows Event XML parsing names these fields `_0`, `_1`, and so on, while Winlogbeat names them `param1`, `param2`, and so on, which match the `%1`, `%2` inserts of the provider's message.

If your queries read `unmapped.EventData._0`, read `unmapped.EventData.param1` instead, and shift every other index by one.
