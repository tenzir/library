---
title: Windows scheduled task, directory access, and script block fixes
type: bugfix
authors:
  - zedoraps
created: 2026-11-25T23:29:25.737365Z
---

Windows events map these fields correctly for every collector:

- Scheduled tasks 4698–4702 get the process ID that Windows writes in `ClientProcessId`. It was read as hexadecimal, so `4052` became `16466`.
- Directory object operations 4662: activity Read when every access only reads, such as `Read Property`, `List Contents`, or `READ_CONTROL`; Update otherwise.
- Script blocks 4104 from Winlogbeat: level `warning` maps to severity Low, as in Windows Event XML.
