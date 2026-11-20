---
title: Process IDs and registry operations from NXLog Community Edition
type: bugfix
authors:
  - zedoraps
created: 2026-11-20T17:43:53.113439Z
---

Windows events from NXLog Community Edition now keep the process IDs, Sysmon registry operations, service accounts, and cleared-log details that NXLog overwrites or drops, so they map to the same OCSF events as natively collected ones.

**NXLog writes** (Community Edition, `to_json()`, Sysmon 12):

```json
{"EventID": 12, "ProcessID": 2716, "EventType": "INFO",
 "Message": "Registry object added or deleted:\r\nRuleName: -\r\nEventType: DeleteValue\r\n...\r\nProcessId: 7012\r\n...",
 "TargetObject": "HKLM\\SOFTWARE\\Example\\Value"}
```

NXLog writes the event data next to its own fields and overwrites event data fields with the same name in any case, such as Sysmon's `ProcessId` with its `ProcessID`, and Sysmon's `EventType` with its severity caption. It drops `UserData` and keeps the XML escaping of event data values.

**OCSF before → now:**

| Event | Field | Before | Now |
|---|---|---|---|
| Sysmon 1, 3, 5, 11, 12, 13, 22, 26 | `actor.process.pid`, `process.pid` | Not set (warning) | From the message |
| Sysmon 12 `DeleteValue` | `class_uid`, `activity_id` | Registry Key Activity, Create | Registry Value Activity, Delete |
| Sysmon 12 `DeleteKey` | `activity_id` | Create | Delete |
| Security 4624, 4657, 4663, 4670, 4688, 4904, 4905, 4907 | `actor.process.pid`, `logon_process.pid`, `process.parent_process.pid` | Not set (warning) | From `Process ID` or `Creator Process ID` in the message |
| Application Error 1000 | `process.pid`, `actor.process.pid` | Not set (warning) | From `Faulting process id` in the message |
| Service Control Manager 7045 | `win_service.service_start_name` | Not set (warning) | `LocalSystem` |
| Eventlog 104 | `log_name`, `actor.user` | Not set (warning) | The cleared log and the user that NXLog resolves |
| Security 1102 | `actor.user`, `actor.session` | Not set | From the subject in the message |
| Command lines, scripts, Sysmon 22 `Image` | XML escaping | `&lt;unknown process&gt;` | `<unknown process>` |

The values come from the rendered English message. On Windows in other languages, these fields stay unset, and the client process of a cleared log is lost in any language.

**Why:** NXLog Community Edition supports neither `AddPrefix` nor `CaptureEventXML`, so its own fields overwrite event data with the same name. Without the process ID, Sysmon, Security, and Application Error events had no process to correlate, and Sysmon registry deletions showed up as key creations.
