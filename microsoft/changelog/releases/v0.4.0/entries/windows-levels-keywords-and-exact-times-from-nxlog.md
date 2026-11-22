---
title: Windows levels, keywords, and exact times from NXLog
type: change
authors:
  - zedoraps
created: 2026-11-20T17:43:53.990321Z
---

Windows events from NXLog now carry the level, keywords mask, provider GUID, and activity ID as Windows writes them, and read epoch times exactly.

- `metadata.log_level` comes from `EventType`: `0` for audit events, `1` to `5` for `CRITICAL` through `VERBOSE`.
- The keywords mask is a hex string such as `0x8020000000000000` instead of a signed integer.
- Provider GUIDs and activity IDs are lowercase, and the activity ID becomes `metadata.correlation_uid`.
- Integer `EventTime` and `EventReceivedTime` are read as microseconds since the Unix epoch. NXLog writes them that way with `Exec $EventTime = integer($EventTime); $EventReceivedTime = integer($EventReceivedTime);`.
- String times without a zone are read as UTC.
