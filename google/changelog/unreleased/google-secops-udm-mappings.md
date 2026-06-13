---
title: Google SecOps UDM mappings
type: feature
authors:
  - mavam
  - codex
prs:
  - 158
created: 2026-06-13T09:55:10.747511Z
---

The Google package now maps between Google SecOps UDM records and OCSF 1.8.0 events.

Use `google::udm::map` to convert OCSF events into UDM event or entity records, and `google::ocsf::map` to convert UDM records back into OCSF:

```tql
google::udm::map
google::ocsf::map
```

The package preserves source-specific fields under `additional` for UDM output and `unmapped` for OCSF output, and includes examples and tests for representative event and entity mappings.
