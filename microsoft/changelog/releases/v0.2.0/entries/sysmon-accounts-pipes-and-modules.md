---
title: Sysmon accounts, pipes, and remote thread modules
type: bugfix
authors:
  - zedoraps
prs:
  - 209
created: 2026-08-29T10:25:02.375909Z
---

Sysmon events report an unresolved account SID in `user.uid` instead of `user.name` and treat `-` as absent. Pipe events name pipes as named pipes, process tampering (25) carries its tampering type, and remote threads (8) describe their start module as a file with its path.
