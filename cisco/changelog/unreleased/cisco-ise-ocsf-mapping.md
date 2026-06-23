---
title: Cisco ISE syslog parsing and OCSF mapping
type: feature
authors:
  - zedoraps
  - claude
prs:
  - 161
created: 2026-06-18T00:00:00Z
---

The `cisco` package now parses Cisco Identity Services Engine (ISE) syslog and
maps parsed ISE events to OCSF.

Use `cisco::ise::parse` to normalize ISE message bodies and
`cisco::ise::reassemble` before parsing when ISE splits a logical message into
numbered syslog segments.

The `cisco::ise::ocsf::map` operator maps Passed Authentications and Failed
Attempts to OCSF Authentication (3002), RADIUS Accounting to OCSF Network
Activity (4001), and all other ISE categories to OCSF Base Events. Incomplete
messages are kept as `cisco.ise.incomplete` Base Events with truncation
metadata instead of being dropped or emitted as complete events.
