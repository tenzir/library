---
title: Authentication method, session, and role fixes in the CIM mapping
type: bugfix
authors:
  - zedoraps
created: 2026-11-20T19:35:09.125391Z
---

CIM Authentication fixes for method, session, and role.

- `authentication_method` is empty for an unknown protocol and never an OCSF protocol ID.
- `session_id` falls back to `session.uid_alt`, never to the actor's session.
- `user_role` and `src_user_role` are gone; they copied the user type.
