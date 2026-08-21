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

The Google package now maps between Google SecOps UDM records and OCSF 1.9.0 events.

Use `google::udm::from_ocsf` to convert OCSF events into UDM event or entity records, and `google::ocsf::from_udm` to convert UDM records back into OCSF:

```tql
google::udm::from_ocsf
google::ocsf::from_udm
```

The mappings keep first-class schema fields and only attach the source record for generic fallback cases. The package includes examples and tests for representative event and entity mappings.
