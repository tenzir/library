---
title: Actors for Service Control Manager events
type: bugfix
authors:
  - zedoraps
created: 2026-11-18T10:40:10.548534Z
---

Service Control Manager events now have an actor when the event names one:

- Service state changes (7036) name the Service Control Manager process.
- Start type changes (7040) and service installations (7045) name the account from the event header.

Service crashes (7034) and terminations with an error (7023) still have no actor, because the service stopped on its own.
