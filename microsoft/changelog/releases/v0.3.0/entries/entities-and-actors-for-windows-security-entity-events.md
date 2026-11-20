---
title: Entities and actors for Windows Security entity events
type: bugfix
authors:
  - zedoraps
created: 2026-11-18T10:40:11.340169Z
---

More Windows Security entity events now identify their entity and actor.

| Event | Before | Now |
|---|---|---|
| 4665/4667 client context | No ID, no actor | Context ID in `entity.uid`, client in `actor.user` |
| 4870 revoked certificate | No ID | Serial number in `entity.uid` |
| 4902 per-user audit policy | No ID | Policy ID in `entity.uid` |
| 4931–4933 replication | No name | Naming context in `entity.name`; 4932/4933 session in `entity.uid`; 4931/4933 `status_code` |
| 4673 privileged service call | No name | Service, or else privileges, in `entity.name` |
| 4661, 4670, 4673, 4674 | No `actor.process` | Subject's process in `actor.process` |
