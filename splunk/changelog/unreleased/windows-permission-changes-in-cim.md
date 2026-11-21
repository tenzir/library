---
title: Windows permission changes in CIM
type: feature
authors:
  - zedoraps
created: 2026-11-21T11:41:26.876459Z
---

Changed object permissions (4670) map to the matching CIM dataset.

- Registry keys: Endpoint Registry, `action=modified`, the key as `registry_path`.
- Other objects: Change, `action=acl_modified`, the object and its type, the subject as `user`.
