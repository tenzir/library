---
title: Accurate Windows logon and logoff events
type: bugfix
authors:
  - zedoraps
prs:
  - 209
created: 2026-08-29T10:25:02.375909Z
---

Logons report the System logon type of Windows (`0`) as OCSF `1`, logoffs report the logon type of the ended session, and failed logons report the failure reason in `status_detail`. Logon process names lose the padding that Windows adds.

Logons without an address or workstation, logoffs, and explicit credential logons from local callers no longer carry empty endpoints or actors. The all-zero logon GUID no longer becomes a session ID that links unrelated sessions.
