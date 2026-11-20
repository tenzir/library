---
title: Removed Windows Account Change mapping operator
type: breaking
authors:
  - zedoraps
created: 2026-11-20T19:45:57.200346Z
---

The `microsoft::windows::ocsf::events::account_change` operator is gone because its events now map to User Management.

| Removed operator | Replacement |
|---|---|
| `account_change` | `user_management` with the User Management `activity_id` |

**What you need to do:** Nothing if you call `microsoft::windows::ocsf::normalize`. If you call `account_change` directly, switch to `user_management`, which takes the same positional arguments, `windows` and `ocsf`, and translate the activity: Create `1` → `1`, Enable `2` → `4`, Password Change `3` → `8`, Password Reset `4` → `9`, Disable `5` → `5`, Delete `6` → `3`, Lock `9` → `6`, Unlock `12` → `7`.
