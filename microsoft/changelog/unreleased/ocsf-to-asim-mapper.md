---
title: OCSF to ASIM mapper
type: feature
authors:
  - mavam
  - codex
prs:
  - 153
created: 2026-06-07T00:00:00Z
---

The Microsoft package now includes `microsoft::asim::map` to convert supported
Microsoft events into flat Microsoft Sentinel ASIM event records. The mapper
uses the new `microsoft::ocsf::map` entry point and `microsoft::asim::ocsf::map`
for validated OCSF 1.8 events.

Microsoft mapping operators now treat the current event as the source event to
map. For raw Windows Event Log XML, first run `this = data.parse_winlog()`;
the resulting structured event can then be normalized through
`microsoft::ocsf::map` or `microsoft::asim::map`. Mapping operators accept an
optional `raw` value when the original source payload is still available and
should be preserved in OCSF `raw_data` and `raw_data_size`.

The mapper covers the Microsoft package's current OCSF authentication, process,
audit, user-management, and alert outputs, plus direct OCSF counterparts for
file, network, DNS, DHCP, and web session ASIM schemas. The full original OCSF
event is preserved under `AdditionalFields` so no source data is lost.
