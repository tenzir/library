---
title: Windows Error Reporting events as Application Error events
type: change
authors:
  - zedoraps
created: 2026-11-18T10:40:08.620297Z
---

Windows Error Reporting events (1001) now map to Application Error (6008), and the report stays in `unmapped.EventData`.

| Event | Before | Now |
|---|---|---|
| 1001 | Process Activity · Terminate · Failure | Application Error · General Error |

**Why:** Most reports concern other problems than crashes, such as Windows Update failures, and Application Error 1000 already reports crashes.
