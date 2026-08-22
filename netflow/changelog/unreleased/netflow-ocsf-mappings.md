---
title: NetFlow OCSF mappings
type: feature
authors:
  - mavam
  - codex
prs:
  - 169
created: 2026-08-01T17:01:03.310754Z
---

The new `netflow` package maps NetFlow v5, NetFlow v9, and IPFIX records to
OCSF 1.9.0:

```tql
accept_udp "0.0.0.0:2055", binary=true
read_netflow
netflow::ocsf::map this, this
ocsf_derive
ocsf_cast
```

Flow records become Network Activity `Traffic` events. The mapper preserves
options records as Base Events, retains source fields without an OCSF
destination under `unmapped`, and marks the connection initiator as unknown.
Flow observation bounds and duration remain within `traffic`.
