---
title: Windows Error Reporting events as Application Error events
type: change
authors:
  - zedoraps
created: 2026-11-18T10:40:08.620297Z
---

Windows Error Reporting events (1001) now map to Application Error instead of Process Activity, which claimed a process termination. The report's event name and problem signature stay in `unmapped`.

Most of these reports concern other problems, such as Windows Update failures or missing drivers, and Application Error 1000 already reports application crashes.
