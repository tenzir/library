---
title: OCSF to ASIM mapper
type: feature
authors:
  - mavam
  - codex
created: 2026-06-07T00:00:00Z
---

The Microsoft package now includes `microsoft::ocsf::map_to_asim` to convert
validated OCSF 1.8 events into flat Microsoft Sentinel ASIM event records.

The mapper covers the Microsoft package's current OCSF authentication, process,
audit, user-management, and alert outputs, plus direct OCSF counterparts for
file, network, DNS, DHCP, and web session ASIM schemas. The full original OCSF
event is preserved under `AdditionalFields` so no source data is lost.
