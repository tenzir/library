---
title: Process creator and original file name in CIM Processes
type: bugfix
authors:
  - zedoraps
created: 2026-11-20T19:37:14.624717Z
---

CIM Processes names the account that spawned a process and keeps the original file name.

- `user`/`user_id` take the creator (`actor.user`), else `process.user`.
- `original_file_name` carries `process.file.internal_name`.
