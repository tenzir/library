---
title: CIM Change actions for event log activity
type: bugfix
authors:
  - zedoraps
created: 2026-11-20T19:40:07.400755Z
---

CIM Change uses the CIM actions for event log activity: `cleared`, `deleted`, `started`, `stopped`, and `restarted` instead of `clear`, `delete`, `start`, `stop`, and `restart`.

- `splunk::ocsf::from_cim` accepts both forms.
