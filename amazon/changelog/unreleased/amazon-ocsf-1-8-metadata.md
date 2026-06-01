---
title: Amazon OCSF 1.8 metadata
type: change
authors:
  - mavam
  - codex
prs:
  - 147
created: 2026-05-31T19:12:55Z
---

Amazon Route 53 and VPC Flow Log mappings now target OCSF 1.8.0, the latest
stable OCSF schema version used by the library.

Downstream tools that inspect OCSF metadata now see `metadata.version` set to
`1.8.0` for Amazon events. Review any consumers that pinned the older metadata
version before comparing mapped events.
