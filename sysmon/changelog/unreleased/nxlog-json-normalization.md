---
title: NXLog JSON normalization
type: feature
authors:
  - mavam
prs:
  - 180
created: 2026-08-27T06:33:48.406501Z
---

Normalize flat Sysmon events from NXLog JSON without rewriting the OCSF mappings:

```tql
from_file "sysmon-nxlog.ndjson" {
  read_ndjson
}
sysmon::ocsf::normalize
```

The existing structured Windows Event Log input remains supported. You can pass `log_format` when adapting another collector to the `System` and `EventData` layout.
