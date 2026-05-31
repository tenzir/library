---
title: Simplify Suricata OCSF mapping
type: change
authors:
  - mavam
  - codex
created: 2026-05-31T15:46:51Z
---

The `suricata::ocsf::map` operator now owns the shared OCSF setup, event
dispatch, and finalization for Suricata EVE JSON events. Event-specific OCSF
operators focus only on class-specific fields, and unknown event types fall back
to OCSF Base Event.

The mapping now preserves more accurate Suricata network direction, maps
`flow_id` as the original event UID, improves HTTP, DHCP, FTP, SMTP, SSH, TLS,
alert, flow, and file activity coverage, and validates all Suricata OCSF test
outputs with `ocsf::cast`.
