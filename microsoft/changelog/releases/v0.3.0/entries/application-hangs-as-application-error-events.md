---
title: Application hangs as Application Error events
type: change
authors:
  - zedoraps
created: 2026-11-19T01:04:49.828007Z
---

Application hangs (1002) now map to Application Error (6008) instead of Process Activity, like Windows Error Reporting events (1001). The hang type, such as `Quiesce`, maps to `status_detail`.

Process Activity requires an `actor`, but the event doesn't say who closed the hung application, the user or Windows, so `ocsf_cast` warned about every hang.

Application Error has no process object, so the hung process stays in `unmapped.EventData` under its source names, such as `AppName`, `ProcessId`, `StartTime`, and `ExeFileName`. Tenzir's Sigma catalog maps no rules for the Application log, so no Sigma rule depends on the previous class.
