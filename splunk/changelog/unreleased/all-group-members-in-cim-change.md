---
title: All group members in CIM Change
type: bugfix
authors:
  - zedoraps
created: 2026-11-20T20:18:21.627173Z
---

CIM Change keeps all members of an OCSF Group Management event instead of only the first.

- `user` lists every member by name, or by ID without a name; `user_name` and `user_type` list the existing names and types.
- A legacy `user` joins unless `users` lists the same account (same `uid`, else same `name`).
- `splunk::ocsf::from_cim` maps member lists back to `users`.
