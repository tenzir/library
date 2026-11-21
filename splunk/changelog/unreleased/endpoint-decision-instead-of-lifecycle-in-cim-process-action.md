---
title: Endpoint decision instead of lifecycle in CIM process action
type: change
authors:
  - zedoraps
created: 2026-11-20T19:38:10.030364Z
---

CIM Processes `action` reports the endpoint decision instead of the lifecycle.

- Denied or Blocked gives `blocked`, Allowed gives `allowed`, a successful launch gives `allowed`; Unknown decides nothing.
- Terminations get no `action`; `splunk::ocsf::from_cim` maps them to activity Other and `allowed` to Launch.

Replace `action=launch` with `action=allowed`.
