---
title: Source-aware OCSF network mappings
type: bugfix
authors:
  - zedoraps
created: 2026-10-28T11:20:31.865025Z
prs:
  - 208
---

Route 53 and VPC Flow Log mappings now construct endpoints only when source identities are available, retaining unused source fields in `unmapped`. Connection direction uses the honest Unknown value when it cannot be determined. VPC `NODATA` and `SKIPDATA` collection statuses become explicit Base Events and retain their cloud profile and account identity. Known network activities keep their classification when required context is missing; OCSF validation reports warnings.
