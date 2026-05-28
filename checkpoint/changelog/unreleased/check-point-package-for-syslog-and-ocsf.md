---
title: Check Point package for syslog and OCSF
type: feature
authors:
  - mavam
  - codex
created: 2026-05-28T10:01:09Z
---

The library now includes a `checkpoint` package for parsing Check Point Log
Exporter records and mapping fixture-backed event families to OCSF.

The package exposes reusable operators for extracting configured Check Point
syslog formats, normalizing Check Point records into a canonical shape, and
mapping them to OCSF, with disabled pipeline templates for onboarding syslog
and publishing mapped OCSF events.

You can parse structured exports or syslog and then map them with the package
operators:

```tql
from "udp://0.0.0.0:514" {
  read_syslog
}
checkpoint::syslog::parse_structured_data
checkpoint::ocsf::map
ocsf::derive
ocsf::cast
```

The syslog parser entry points are explicit for each configured feed format.
After extraction, `checkpoint::parse` normalizes aliases, timestamps, IPs,
ports, counters, durations, NAT fields, user fields, and Check Point
match-table fields before the OCSF mapper performs shared setup, dispatch, and
source-residue handling.

The mapper now covers these fixture-backed OCSF classes:

| Check Point family | OCSF class |
|---|---|
| Firewall/Core/VPN-1 traffic | Network Activity (4001) |
| Application Control and URL Filtering | Web Resource Access Activity (6004) |
| IPS and threat-prevention findings | Detection Finding (2004) |
| DLP and Content Awareness | Data Security Finding (2006) |
| VPN and Mobile Access | Tunnel Activity (4014) |
| MTA, Anti-Spam, and Email Security | Email Activity (4009) |
| WEB_API management events | API Activity (6003) |
| SmartConsole/Web UI management changes | Entity Management (3004) |
