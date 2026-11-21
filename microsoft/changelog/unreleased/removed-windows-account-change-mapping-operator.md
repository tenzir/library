---
title: Removed Windows Account Change mapping operator
type: breaking
authors:
  - zedoraps
created: 2026-11-20T19:45:57.200346Z
---

The `microsoft::windows::ocsf::events::account_change` operator is gone because its events now map to User Management. `microsoft::windows::ocsf::normalize` is unaffected; direct callers use `user_management` with the same `windows` and `ocsf` arguments and a User Management `activity_id`.
