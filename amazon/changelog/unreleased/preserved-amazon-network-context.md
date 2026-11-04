---
title: Preserved Amazon network context
type: bugfix
prs:
  - 215
created: 2026-11-04T15:17:58.603591Z
---

Route 53 and VPC Flow Log mappings now construct endpoints only when the source identifies them, retaining unused values under their original keys in `unmapped`. Missing connection direction maps to Unknown. VPC `NODATA` and `SKIPDATA` collection statuses become Base Events and preserve their cloud account and network-interface context.
