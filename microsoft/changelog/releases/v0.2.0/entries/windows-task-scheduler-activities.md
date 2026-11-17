---
title: Task Scheduler actors and launch activities
type: change
authors:
  - zedoraps
prs:
  - 209
created: 2026-08-29T10:25:02.375909Z
---

Task Scheduler events take the actor from the user context, from the user that changed a registration (140–142), or from the scheduler account. The PIDs of launched task processes stay in `unmapped` instead of appearing as the actor.

Launch requests by users (110) and queued launches (325) are now Scheduled Job Activity events, and Other activities name the source activity.
