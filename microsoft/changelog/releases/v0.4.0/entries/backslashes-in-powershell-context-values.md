---
title: Backslashes in PowerShell context values
type: bugfix
authors:
  - zedoraps
prs:
  - 256
created: 2026-11-21T17:55:23.001313Z
---

PowerShell 4100 and 4103 events keep the backslashes in the host application, script path, and user of their context, so `CORP\nora` maps to the user `nora` in the domain `CORP`, and `C:\temp\new.ps1` stays a path.
