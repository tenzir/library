---
title: PowerShell engine errors as Application Error events
type: change
authors:
  - zedoraps
prs:
  - 209
created: 2026-08-29T10:25:02.375909Z
---

PowerShell engine errors (4100) are now Application Error events instead of Script Activity, because they report an error message rather than a script. The error lands in `message`, and the event reports the host command line and the user instead of treating the context block as the script.
