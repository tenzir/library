---
title: Lossless historical authentication aggregation
type: bugfix
authors:
  - zedoraps
created: 2026-10-28T11:20:37.174376Z
prs:
  - 200
  - 208
  - 205
---

OpenSSH aggregation retains authentication records when processing bulk historical input and correlating parent and child sessions. Authentication observations keep their known class and activity when a user is missing. OCSF validation reports the missing user as a warning while preserving the event.
