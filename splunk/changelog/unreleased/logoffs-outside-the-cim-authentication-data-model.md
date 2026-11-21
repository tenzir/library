---
title: Logoffs outside the CIM Authentication data model
type: change
authors:
  - zedoraps
created: 2026-11-20T19:35:37.067938Z
---

OCSF Authentication logoffs, such as Windows 4634/4647, no longer count as sign-ins.

- Logoffs get the tags `access`, `stop`, and `logoff` instead of `authentication`.
