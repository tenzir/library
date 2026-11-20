---
title: Application hangs and error reports as Application Error
type: change
authors:
  - zedoraps
created: 2026-11-18T10:40:08.620297Z
---

Windows Error Reporting events (1001) and application hangs (1002) now map to Application Error (6008).

| Event | Before | Now |
|---|---|---|
| 1001 Windows Error Reporting | Process Activity · Terminate · Failure | Application Error · General Error |
| 1002 application hang | Process Activity · Terminate · Failure | Application Error · General Error, hang type in `status_detail` |

The report and the hung process stay in `unmapped.EventData`:

```tql
status_detail: "Quiesce",
unmapped: {EventData: {AppName: "ExampleViewer.exe", ProcessId: "0x23c8"}},
```

**Why:** Most error reports concern other problems than crashes, such as Windows Update failures, and Application Error 1000 already reports crashes. Process Activity requires an `actor`, but a hang event doesn't say whether the user or Windows closed the application.
