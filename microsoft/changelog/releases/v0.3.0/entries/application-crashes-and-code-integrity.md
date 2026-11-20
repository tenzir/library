---
title: Application crashes and Code Integrity
type: bugfix
authors:
  - zedoraps
created: 2026-11-18T10:40:09.905177Z
---

Application crashes (1000) now map the values that Windows writes, with or without field names, Code Integrity events now give the loading process its process and thread ID, and App Control audit and block events (3076/3077) now map the file, the loading process, and the signing levels.

| Event | Field | Before | Now |
|---|---|---|---|
| 1000 crash | `module.file` | Positional data only | Also `ModuleName`, `ModulePath` |
| 1000 crash | `module.load_type_id` | Not set | `0` (Unknown) |
| 1000 crash | `actor.process` | Not set | The crashed process |
| 1000 crash | `process.pid` without hex letters, such as `2048` | Read as decimal | Read as hexadecimal |
| Code Integrity | `actor.process.pid`, `ptid` | Not set | From the event header |
| Code Integrity | `actor.process` without a header process ID | Path only | Not set; the name stays in `unmapped.EventData` |
| 3076/3077 App Control | `application.name`, `application.data.file_path` | Empty | From `File Name` |
| 3076/3077 App Control | `actor.process` | Missing | From `Process Name` |
| 3076/3077 App Control | `application.data.requested_signing_level`, `validated_signing_level` | Empty | From `Requested Signing Level`, `Validated Signing Level` |

Sigma rules that read `FileNameBuffer`, `ProcessNameBuffer`, or the signing levels now see these values.

**Why:** Code Integrity writes these events in the context of the loading process, and an OCSF process needs a `pid`, `uid`, or `cpid`.
