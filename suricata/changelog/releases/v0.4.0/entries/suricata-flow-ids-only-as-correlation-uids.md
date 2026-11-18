---
title: Suricata flow IDs only as correlation UIDs
type: breaking
authors:
  - zedoraps
created: 2026-11-18T11:53:49.121818Z
---

Suricata events no longer set `metadata.original_event_uid`. OCSF defines this attribute as the identifier of the one raw log entry an event came from, but Suricata's `flow_id` identifies a flow, which the `flow`, `alert`, `http`, `fileinfo`, and other events of that flow share. Use `metadata.correlation_uid` instead, which holds the same value and exists to link related events. Network events also keep the flow ID in `connection_info.uid`.

Before:

```tql
where metadata.original_event_uid == "1349859816939076"
```

After:

```tql
where metadata.correlation_uid == "1349859816939076"
```
