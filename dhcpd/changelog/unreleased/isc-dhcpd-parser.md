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

The library now includes a `dhcpd` package with `dhcpd::parse` for normalizing
ISC DHCPD log message records and `dhcpd::ocsf::map` for mapping parsed DHCP
transaction records to OCSF DHCP Activity.

The package documents current mapper limits up front: failover binding-update
messages, lease cache/reuse decisions, pool threshold and adaptive lease-time
diagnostics, debug lease-selection traces, and daemon/config/internal diagnostics
are currently retained as OCSF Base Event records instead of being expanded into
dedicated schemas.

The parser expects input records with required `time` and raw `message` fields,
because DHCPD message bodies do not include their own timestamp. The raw message
body is preserved as `raw_data`; parser diagnostics are kept in the mapped
event's `unmapped` object instead of being reported as DHCP transaction
failures.
