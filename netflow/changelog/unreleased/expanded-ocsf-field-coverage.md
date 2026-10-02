---
title: Expanded OCSF 1.9 field coverage
type: change
authors:
  - mavam
prs:
  - 191
created: 2026-10-02T14:34:35.621972Z
---

NetFlow and IPFIX OCSF events now expose ingress and egress interface identifiers and source/destination VLAN identifiers on their network endpoints. Exporter, sampling, and template context remains in `unmapped`.
