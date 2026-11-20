---
title: Unknown load type for Sysmon modules
type: bugfix
authors:
  - zedoraps
created: 2026-11-19T00:57:22.99909Z
---

Sysmon image loads (7) and remote thread creations (8) without a start function now set `module.load_type_id` to `0` (Unknown).

**Why:** OCSF requires a module to have a load type or a function name, and Sysmon doesn't report how a module was loaded.
