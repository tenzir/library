---
title: Microsoft Graph devices and risky users
type: bugfix
authors:
  - zedoraps
created: 2026-11-18T10:40:14.472305Z
---

Microsoft Graph sign-ins and Intune managed devices now set the operating system type from the reported platform, and Microsoft Entra ID risky users now identify their owner.

**Microsoft Graph writes:**

```json
// Sign-in: the device's platform, by name
{"deviceDetail": {"deviceId": "device-1", "operatingSystem": "Windows 11"}}
// Intune managed device
{"operatingSystem": "Windows", "osVersion": "11.0.26100"}
// Risky user: id is the ID of the user at risk
{"id": "user-1", "userDisplayName": "Alice Example"}
```

**OCSF before → now:**

| Source | Field | Before | Now |
|---|---|---|---|
| Sign-ins, managed devices | `src_endpoint.os.type_id` (sign-ins), `device.os.type_id` (managed devices) | Not set (warning) | Such as `100` (Windows) for `Windows 11` |
| Sign-ins, managed devices, unrecognized platform | Same | Not set | `99` (Other), name in `os.type` |
| Entra ID risky users | `resources[].owner.uid` | Not set; the owner had only `full_name` (warning) | The risky user's `id`, which Microsoft Graph defines as the ID of the user at risk |

**Why:** Microsoft Graph reports the platform only as a name, with varying case and often a version, while an OCSF operating system requires a type ID, so the mapping derives it from the start of the name. For risky users, the owner had only a display name, which doesn't identify an OCSF user, but the record's `id` does.
