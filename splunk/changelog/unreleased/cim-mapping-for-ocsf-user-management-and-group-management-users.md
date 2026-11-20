---
title: CIM mapping for OCSF User Management and Group Management users
type: change
authors:
  - zedoraps
created: 2026-11-20T19:45:57.879111Z
---

`splunk::cim::from_ocsf` now maps OCSF User Management (3007) events to the Change Account Management data model like Account Change (3001), and reads the member of a Group Management (3006) event from `users`, which supersedes `user` in OCSF 1.9.

**What changes:**

- User Management events, such as Windows account creation, lockout, and privilege assignment, now produce Change Account Management fields instead of passing through unmapped.
- Group membership changes that list the member in `users` now fill `user`, `user_name`, and `user_type`. Events that still use `user` map as before.
