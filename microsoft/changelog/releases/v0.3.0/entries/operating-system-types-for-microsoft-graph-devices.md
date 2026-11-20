---
title: Operating system types for Microsoft Graph devices
type: bugfix
authors:
  - zedoraps
created: 2026-11-18T10:40:14.472305Z
---

Microsoft Graph sign-ins and Intune managed devices now set the operating system type from the reported platform.

| Field | Before | Now |
|---|---|---|
| `src_endpoint.os.type_id` (sign-ins), `device.os.type_id` (managed devices) | Not set | Such as `100` (Windows) for `Windows 11` |
| Same, unrecognized platform | Not set | `99` (Other), name in `os.type` |
