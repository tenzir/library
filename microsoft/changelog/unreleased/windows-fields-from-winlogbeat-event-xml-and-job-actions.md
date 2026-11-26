---
title: Windows fields from Winlogbeat event XML and job actions
type: change
authors:
  - zedoraps
created: 2026-11-26T09:11:29.011936Z
---

Some Windows fields change:

- Winlogbeat events with `include_xml: true` come from their event XML, like natively collected events. `metadata.log_level` changes from Winlogbeat's level text, such as `information`, to the numeric Windows level, such as `4`. Task and opcode in `unmapped` become numbers, and Winlogbeat fields that repeat the XML leave `unmapped`.
- Scheduled tasks 4698–4702 report each Exec action as a job action in `job.job_actions`, with its working directory, instead of the deprecated `job.cmd_line`.
