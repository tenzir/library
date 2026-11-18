---
title: Zeek connection UIDs only as correlation UIDs
type: breaking
authors:
  - zedoraps
created: 2026-11-18T11:53:20.79362Z
---

Zeek events no longer set `metadata.original_event_uid`. OCSF defines this attribute as the identifier of the one raw log entry an event came from, but Zeek's `uid` identifies a connection, which many records across `conn.log`, `smtp.log`, `files.log`, and other logs share. Use `metadata.correlation_uid` instead, which holds the same value and exists to link related events. Network events also keep the connection UID in `connection_info.uid`.

Before:

```tql
where metadata.original_event_uid == "CmRFd61N7G7YA909D1"
```

After:

```tql
where metadata.correlation_uid == "CmRFd61N7G7YA909D1"
```
