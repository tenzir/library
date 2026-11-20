---
title: Actors for Service Control Manager events
type: bugfix
authors:
  - zedoraps
created: 2026-11-18T10:40:10.548534Z
---

Service Control Manager events now have an actor when the event names one.

| Event | Before | Now |
|---|---|---|
| 7036 state change | No actor | Service Control Manager `pid` and `ptid` in `actor.process` |
| 7040 start type change, 7045 installation | No actor | Header account in `actor.user` |

Crashes (7034) and terminations with an error (7023) still have no actor, because the service stopped on its own.
