---
title: Application hangs as Application Error events
type: change
authors:
  - zedoraps
created: 2026-11-19T01:04:49.828007Z
---

Application hangs (1002) now map to Application Error (6008), like Windows Error Reporting (1001).

| Event | Before | Now |
|---|---|---|
| 1002 | Process Activity · Terminate · Failure | Application Error · General Error, hang type in `status_detail` |

The hung process stays in `unmapped.EventData`:

```tql
status_detail: "Quiesce",
unmapped: {EventData: {AppName: "ExampleViewer.exe", ProcessId: "0x23c8"}},
```

**Why:** Process Activity requires an `actor`, but the event doesn't say whether the user or Windows closed the application.
