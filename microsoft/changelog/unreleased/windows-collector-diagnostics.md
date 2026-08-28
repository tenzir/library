---
title: Windows collector diagnostics
type: change
authors:
  - zedoraps
created: 2026-08-27T00:00:00Z
---

Normalize Windows events from Winlogbeat and Fluent Bit without warnings when
collector fields are absent or represented as strings. The Windows OCSF mapper
now converts ports, IP addresses, result codes, logon types, file versions, and
other collector-dependent values to their target types. It also accepts Fluent
Bit events that contain positional `StringInserts` instead of an `EventData`
map, including Service Control Manager event 7045.

Correct OCSF mappings for source-specific authentication protocols, PowerShell
script content, registry values of unknown type, Windows services, scheduled
task actions, process sessions, and incomplete application or parent-process
data.
