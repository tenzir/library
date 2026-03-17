---
title: Check Point package for syslog and OCSF
type: feature
authors:
  - mavam
  - codex
created: 2026-03-17T09:59:59.453277Z
---

The library now includes a `checkpoint` package for parsing Check Point firewall logs and mapping common events to OCSF.

You can onboard either structured exports or syslog and then normalize them with the package operators:

```tql
from "udp://0.0.0.0:514" {
  read_syslog
}
checkpoint::parse
checkpoint::ocsf::map
```

The package covers raw Check Point syslog parsing, normalization of firewall traffic and detection records, and tested OCSF mappings for `network_activity` and `detection_finding`.
