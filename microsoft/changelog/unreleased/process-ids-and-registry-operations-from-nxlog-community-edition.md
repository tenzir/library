---
title: Process IDs and registry operations from NXLog Community Edition
type: bugfix
authors:
  - zedoraps
created: 2026-11-20T17:43:53.113439Z
---

Windows events from NXLog Community Edition now keep the values that NXLog overwrites or drops.

- Sysmon 1, 3, 5, 11, 12, 13, 22, and 26 get their process IDs again.
- Security 4624, 4657, 4663, 4670, 4688, 4904, 4905, and 4907 get the actor, logon, and parent process IDs.
- Application Error 1000 gets the faulting process ID.
- Sysmon 12 `DeleteKey` and `DeleteValue` map to Delete instead of Create, and `DeleteValue` maps to Registry Value Activity.
- 7045 keeps the service account.
- 104 gets the cleared log and the user, and 1102 gets the subject.
- XML escaping in event data is decoded, so `&lt;unknown process&gt;` becomes `<unknown process>`.
- Values recovered from the message require English Windows.
