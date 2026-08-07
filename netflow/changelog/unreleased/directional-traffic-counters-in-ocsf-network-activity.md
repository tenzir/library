---
title: Directional traffic counters in OCSF Network Activity
type: feature
authors:
  - mavam
  - claude
prs:
  - 173
created: 2026-08-07T21:06:18.934298Z
---

The NetFlow package now maps directional traffic counters to OCSF. Mapped
Network Activity events carry the source-to-destination byte and packet counts
in `traffic.bytes_out` and `traffic.packets_out`, populated from
`octet_delta_count` and `packet_delta_count` of the unidirectional flow record.
Biflow exporters that report both directions via `initiator_octets`,
`responder_octets`, `initiator_packets`, and `responder_packets` additionally
populate `traffic.bytes_in` and `traffic.packets_in`, with `traffic.bytes` and
`traffic.packets` holding the two-way totals.

This aligns the NetFlow mapping with the Zeek and Suricata packages, where
`traffic.bytes_out` already carries originator bytes, so detectors can read
one directional field across all three sources.
