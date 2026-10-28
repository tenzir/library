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

OpenSSH aggregation now retains authentication records when processing bulk historical input and correlating parent and child sessions. Incomplete endpoint details remain in unmapped data. Authentication observations without a user become Base Events with their original mapping preserved.
