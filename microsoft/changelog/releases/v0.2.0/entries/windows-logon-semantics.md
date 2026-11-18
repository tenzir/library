---
title: Accurate Windows logon and logoff events
type: bugfix
authors:
  - zedoraps
prs:
  - 209
created: 2026-08-29T10:25:02.375909Z
---

Logons report the System logon type of Windows (`0`) as OCSF `1`, logoffs report the logon type of the ended session, and failed logons report the failure reason in `status_detail`. Logon process names lose the padding that Windows adds. The logon process carries the PID and image of the process that attempted the logon, because that process registered the logon process name with the LSA.

Logons without an address or workstation, logoffs, and explicit credential logons from local callers no longer carry empty endpoints or actors, and network logons without a local process no longer report a process with PID 0 and path `-`. The all-zero logon GUID no longer becomes a session ID that links unrelated sessions.
