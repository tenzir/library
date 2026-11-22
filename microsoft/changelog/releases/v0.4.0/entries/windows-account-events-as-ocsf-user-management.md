---
title: Windows account events as OCSF User Management
type: change
authors:
  - zedoraps
created: 2026-11-20T19:45:56.225751Z
---

Windows account events now map to OCSF User Management (3007) instead of the deprecated Account Change (3001), and group membership changes list the member in `users` instead of the deprecated `user`.

- 4720/4741 → Create (`1`), 4722 → Enable (`4`), 4723 → Password Change (`8`), 4724 → Password Reset (`9`), 4725 → Disable (`5`), 4726/4743 → Delete (`3`), 4740 → Lock (`6`), 4767 → Unlock (`7`).
- 4728/4729, 4732/4733, 4746/4747, 4751/4752, 4756/4757, and 4761/4762 keep Group Management, with the member in a one-element `users` list.

Sigma rules on these account events and on `MemberName`/`MemberSid` need a Tenzir version whose `sigma` operator reads User Management and `users`.
