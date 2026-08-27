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
  read_ndjson unflatten_separator="."
}
sysmon::ocsf::normalize
metadata.log_format = "json"
```

Configure NXLog with `AddPrefix TRUE` so provider fields remain distinct from collector metadata. The normalizer also accepts Windows Event Log XML directly. For staged processing, use `sysmon::canonicalize` to produce the canonical Windows Event Log structure, then pass the result to `sysmon::ocsf::map`. Add `metadata.log_format`, `raw_data`, and `raw_data_size` in the calling pipeline, where the source format and payload are known.
