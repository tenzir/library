---
title: ISC DHCPD OCSF package
type: feature
authors:
  - raxyte
  - codex
prs:
  - 160
created: 2026-06-18T00:00:00Z
---

The library now includes a `dhcpd` package that normalizes ISC DHCPD messages
to OCSF 1.9.

Use `dhcpd::ocsf::normalize` to take a record with `time` and a raw `message`
body all the way to OCSF. The normalizer preserves the body in `raw_data`. Use
`dhcpd::parse` and `dhcpd::ocsf::map` with separate input and output fields when
a pipeline needs to inspect or enrich the structured DHCPD event before
mapping.

The package expands DHCPv4, DHCP4o6, BOOTP, and DHCPv6 transaction messages.
Failover binding updates, lease cache and reuse decisions, pool threshold and
adaptive lease-time diagnostics, debug lease-selection traces, and daemon or
configuration diagnostics become OCSF Base Event records. Parser diagnostics
remain in the mapped event's `unmapped` object instead of appearing as DHCP
transaction failures.
