---
title: Check Point package for syslog and OCSF
type: feature
authors:
  - mavam
  - codex
created: 2026-05-28T09:02:43Z
---

The library now includes a `checkpoint` package for parsing Check Point firewall
logs and mapping firewall traffic and detection events to OCSF.

The package exposes reusable operators for extracting configured Check Point
syslog formats, normalizing firewall records into a canonical shape, and
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
After extraction, `checkpoint::parse` normalizes timestamps, protocol names, and
Check Point match-table fields before the OCSF mapper performs shared setup,
dispatch, and source-residue handling. Event-specific mapping lives under
`checkpoint::ocsf::events::*`.
