---
title: Unknown load type for Sysmon modules
type: bugfix
authors:
  - zedoraps
created: 2026-11-19T00:57:22.99909Z
---

Sysmon image loads (7) now set `module.load_type_id` to 0 (Unknown), and remote thread creations (8) do so when Sysmon names no start function. A remote thread with a start function, such as `CtrlRoutine`, keeps it in `module.function_name` and needs no load type.

Sysmon doesn't report how a module was loaded, and OCSF requires a module to have a load type or a function name, so `ocsf_cast` warned about these events.
