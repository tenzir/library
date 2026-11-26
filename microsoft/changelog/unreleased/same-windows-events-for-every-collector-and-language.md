---
title: Same Windows events for every collector and language
type: bugfix
authors:
  - zedoraps
created: 2026-11-26T02:48:29.950263Z
---

Windows events map the same for every collector and language:

- Windows Event XML keeps the line breaks of values, such as PowerShell script blocks, and the binary data, such as the service state of Service Control Manager events.
- Winlogbeat events with `include_xml: true` come from their event XML, Winlogbeat records parsed with `parse_json(raw=true)` keep their time, and German audit keywords keep the outcome.
- Service Control Manager events of German Windows map their states and start and service types, and 7036 reads the state from its language-independent binary data.
- Client addresses that are not IP addresses, such as host names, stay in `unmapped`.
- Directory access rights `Delete Child`, `Write Self`, and `List Object` of 4662 render by name.
- Scheduled tasks 4698–4702 report their command as a job action instead of the deprecated `job.cmd_line`.
