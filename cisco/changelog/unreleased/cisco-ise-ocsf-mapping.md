---
title: Cisco ISE syslog parsing and OCSF mapping
type: feature
authors:
  - zedoraps
prs:
  - 161
created: 2026-06-18T00:00:00Z
---

The `cisco` package reassembles and parses Cisco Identity Services Engine (ISE) syslog and maps it to OCSF 1.9:

```tql
accept_tcp "0.0.0.0:514" {
  read_syslog accept_pri_only=true
}
cisco::ise::ocsf::normalize
```

- Segments join per ISE node and message ID within 5 seconds of the first one, configurable with `span`. Complete messages leave with their last segment. Incomplete ones follow as Base Events after two to three spans, or four when no more segments arrive.
- Network access, guest, MDM, and device administration logins and logins to ISE → Authentication (3002); session authorization → Authorize Session (3003).
- Commands on network devices, authorized or executed → Script Activity (1009).
- RADIUS accounting → Network Activity (4001).
- Configuration changes and registered devices → Entity Management (3004); passwords and guest accounts → User Management (3007).
- Log deletion, processes, server reloads, and profiled endpoints → Event Log Activity (1008), Application Lifecycle (6002), Device Power State Activity (1011), and Device Inventory Info (5001).
- Alarms, diagnostics, and other messages → Base Event.
