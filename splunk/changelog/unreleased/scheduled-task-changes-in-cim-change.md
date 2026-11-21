---
title: Scheduled task changes in CIM Change
type: feature
authors:
  - zedoraps
created: 2026-11-20T21:09:14.352377Z
---

Scheduled job changes, such as Windows 4698-4702 and TaskScheduler 106/140/141/142, map to CIM Change.

- `action` is `created`, `modified`, or `deleted`, `object` the job; job runs still pass through.
