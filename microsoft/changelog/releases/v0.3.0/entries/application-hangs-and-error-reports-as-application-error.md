---
title: Application hangs and error reports as Application Error
type: change
authors:
  - zedoraps
created: 2026-11-18T10:40:08.620297Z
---

Windows Error Reporting events (1001) and application hangs (1002) now map to Application Error (6008).

#### Windows Error Reporting

**Windows writes** (Windows Error Reporting 1001, values without names):

```xml
<Provider Name="Windows Error Reporting"/>  <EventID>1001</EventID>
<Data>ServiceHang</Data>      <!-- third value: what Windows reported -->
<Data>ExampleSyncSvc</Data>   <!-- sixth value onward: the problem signature -->
<Data>examplesync.dll</Data>
```

**OCSF before → now:**

| | Before | Now |
|---|---|---|
| Class and activity | Process Activity · Terminate · Failure | Application Error · General Error |
| Severity | Medium | Informational |
| Process | Empty `process`, no `actor` (warnings) | Not set; the report stays in `unmapped.EventData` |

**Why:** 1001 says that Windows filed a problem report, and the third value says what for: `APPCRASH` for a crash, which Application Error 1000 already reports, and most often other problems, such as `ServiceHang` or Windows Update failures. No process terminated, so Process Activity doesn't fit.

#### Application hangs

**Windows writes** (Application Hang 1002):

```xml
<Provider Name="Application Hang"/>  <EventID>1002</EventID>
<Data Name="AppName">ExampleViewer.exe</Data>
<Data Name="ProcessId">0x23c8</Data>
<Data Name="HangType">Quiesce</Data>          <!-- kind of hang -->
```

**OCSF before → now:**

| | Before | Now |
|---|---|---|
| Class and activity | Process Activity · Terminate · Failure | Application Error · General Error |
| Hang type | Not set | `Quiesce`, in `status_detail` |
| Process | Empty `process` for named data, no `actor` (warnings) | Not set |

The report and the hung process stay in `unmapped.EventData`:

```tql
status_detail: "Quiesce",
unmapped: {EventData: {AppName: "ExampleViewer.exe", ProcessId: "0x23c8"}},
```

**Why:** 1002 says that an application stopped responding, but not who ended it. Process Activity requires an `actor`, but a hang event doesn't say whether the user or Windows closed the application.
