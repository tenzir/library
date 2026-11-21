---
title: Connection actor and event log device in CIM
type: bugfix
authors:
  - zedoraps
created: 2026-11-20T19:39:39.691508Z
---

CIM keeps the actor of connections and the device of event log changes.

- Network Traffic: `user` falls back to `actor.user`; `process_id` and `process_guid` carry the actor process.
- Change for event log activity: `dest` falls back to the device.
