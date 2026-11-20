---
title: Entities and actors for Windows Security entity events
type: bugfix
authors:
  - zedoraps
created: 2026-11-18T10:40:11.340169Z
---

More Windows Security entity events now identify their entity and actor:

- Authorization Manager client contexts (4665/4667) use the client context ID and the client account.
- Revoked certificates (4870) use the serial number.
- Per-user audit policy tables (4902) use the policy ID.
- Directory replication events (4931–4933) use the naming context and the replication session. Replication results (4931/4933) also set `status_code` and `status_id`.
- Privileged service calls (4673) name the called service, or the exercised privileges when the event names no service.

Events that report the subject's process, such as 4661, 4670, 4673, and 4674, now carry it in `actor.process`.
