---
title: Cisco Secure Firewall ASA support
type: feature
authors:
  - zedoraps
prs:
  - 162
created: 2026-06-18T00:00:00Z
---

`cisco::asa::read` and `cisco::asa::parse` parse Cisco Secure Firewall ASA syslog, and `cisco::asa::ocsf::normalize` maps it to OCSF 1.9:

- Built, torn down, and reset connections, address translations, access-list and packet denies, module drops, and Botnet Traffic Filter hits → Network Activity (4001).
- Device, AAA, cut-through proxy, and WebVPN logins and logouts → Authentication (3002).
- AnyConnect, IKEv2, and other VPN sessions → Tunnel Activity (4014).
- Executed commands → Script Activity (1009).
- Local user changes → User Management (3007).
- Intrusion signatures and threat detection → Detection Finding (2004).
- Other messages → Base Event, with the message ID in `metadata.event_code` as for all messages.

The parser accepts headers with and without priority, timestamp, year, time zone, and device ID, the EMBLEM and RFC 5424 formats, and messages that a syslog relay or log shipper already parsed. The `timezone` argument sets the time zone of times without one, and `reference` dates old logs without a year.
