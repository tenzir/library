---
title: Microsoft Graph devices and risky users
type: bugfix
authors:
  - zedoraps
created: 2026-11-18T10:40:14.472305Z
---

Microsoft Graph sign-ins and Intune managed devices now set the operating system type from the reported platform, and Microsoft Entra ID risky users now identify their owner.

| Source | Field | Before | Now |
|---|---|---|---|
| Sign-ins, managed devices | `src_endpoint.os.type_id` (sign-ins), `device.os.type_id` (managed devices) | Not set | Such as `100` (Windows) for `Windows 11` |
| Sign-ins, managed devices, unrecognized platform | Same | Not set | `99` (Other), name in `os.type` |
| Entra ID risky users | `resources[].owner.uid` | Not set | The risky user's `id`, which Microsoft Graph defines as the ID of the user at risk |

**Why:** The owner had only a display name, which doesn't identify an OCSF user.
