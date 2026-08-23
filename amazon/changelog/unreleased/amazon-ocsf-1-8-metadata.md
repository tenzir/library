---
title: Amazon OCSF 1.9 mappings
type: change
authors:
  - mavam
  - codex
prs:
  - 147
created: 2026-05-31T19:12:55Z
---

Amazon Route 53 and VPC Flow Log mappings now target OCSF 1.9. VPC observation
windows use `traffic.start_time` and `traffic.end_time`, and Route 53 query logs
use the OCSF DNS query or response activity that matches their contents.
