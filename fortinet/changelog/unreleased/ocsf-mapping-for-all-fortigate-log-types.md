---
title: OCSF mapping for all FortiGate log types
type: feature
authors:
  - mavam
  - claude
prs:
  - 140
  - 147
created: 2026-03-21T17:28:46.407793Z
---

FortiGate logs can now be mapped to OCSF using `fortinet::fortigate::ocsf::map`:

```tql
from_file "fortigate.log" {
  read_lines
}
fortinet::fortigate::ocsf::map line
ocsf::derive
ocsf::cast
```

All major FortiGate log types are covered:

| Log type | OCSF class |
|---|---|
| `traffic/*` | Network Activity (4001) |
| `utm/dns` | DNS Activity (4003) |
| `utm/ips`, `utm/anomaly`, `utm/virus`, `utm/dlp` | Detection Finding (2004) |
| `utm/ssh` | SSH Activity (4007) |
| `utm/ssl` | Network Activity (4001) |
| `utm/webfilter` | HTTP Activity (4002) |
| `utm/emailfilter` | Email Activity (4009) |
| `utm/app-ctrl` | Network Activity (4001) |
| `utm/cifs` | SMB Activity (4006) |
| `event/user`, `event/system` | Authentication (3002) |
| `event/vpn`, `event/endpoint` | Tunnel Activity (4014) |
| `event/wad` | Network Activity (4001) |
| `event/wireless` | Detection Finding (2004) |
| `event/connector`, `event/ha`, `event/fortiextender`, `event/router`, `event/security-rating` | Base Event |

The mapping handles NAT (`trandisp`/`transip` → `proxy_endpoint`), interface zones (`srcintfrole`/`dstintfrole` → `endpoint.zone`), UTM risk scores (`crscore`/`crlevel` → `risk_score`/`risk_level_id`), and session timestamps (`duration` → `traffic.start_time`/`end_time`). Network context for Detection Finding events is placed in `evidences` rather than top-level endpoint fields.
