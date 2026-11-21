---
title: Windows account and group enumeration in CIM Change
type: feature
authors:
  - zedoraps
created: 2026-11-21T11:41:27.726382Z
---

Windows account and group enumerations (4797/4798/4799) map to CIM Change Account Management with `action=read`.

- `user` and `object`/`object_id` are the enumerated account or group, `src_user` the enumerating account, `command` the caller process.
