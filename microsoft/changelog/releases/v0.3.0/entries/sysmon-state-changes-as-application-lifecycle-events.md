---
title: Sysmon state changes as Application Lifecycle events
type: change
authors:
  - zedoraps
created: 2026-11-19T01:01:49.320307Z
---

Sysmon service state changes (4) now map to Application Lifecycle (6002), with Sysmon and its version in `application`.

| Event | Before | Now |
|---|---|---|
| 4 `Started` | Windows Service Activity · Start | Application Lifecycle · Start |
| 4 `Stopped` | Windows Service Activity · Stop | Application Lifecycle · Stop |
| 4 other states | Windows Service Activity · Stop | Application Lifecycle · Other |

No Sigma rule is affected: Tenzir's Sigma catalog has no family for `sysmon_status`.

**Why:** The event names neither the service configuration nor an actor, both of which Windows Service Activity requires.
