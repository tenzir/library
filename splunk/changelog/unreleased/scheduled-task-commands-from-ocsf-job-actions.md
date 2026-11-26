---
title: Scheduled task commands from OCSF job actions
type: bugfix
authors:
  - zedoraps
created: 2026-11-26T02:48:38.741137Z
---

The CIM `command` of a scheduled job comes from the command line of its first OCSF job action, and from the deprecated `job.cmd_line` otherwise.
