---
title: Cisco Secure Firewall ASA support
type: feature
authors:
  - zedoraps
prs:
  - 162
created: 2026-06-18T00:00:00Z
---

`cisco::asa::ocsf::normalize` turns Cisco Secure Firewall ASA syslog into OCSF 1.9, and `cisco::asa::parse` and `cisco::asa::ocsf::map` do it in stages:

- Built, torn down, and reset connections, address translations, access-list and packet denies, module drops, and Botnet Traffic Filter hits → Network Activity (4001).
- Device, AAA, cut-through proxy, and WebVPN logins and logouts → Authentication (3002).
- AnyConnect, IKEv2, and other VPN sessions → Tunnel Activity (4014).
- Executed commands → Script Activity (1009).
- Local user changes → User Management (3007).
- Intrusion signatures and threat detection → Detection Finding (2004).
- Other messages and other input → Base Event. `metadata.event_code` has the message ID.

The operators accept raw lines, the output of `read_syslog`, and messages of log shippers, with and without priority, timestamp, year, time zone, and device ID, in the EMBLEM and RFC 5424 formats, and behind a relay. The `timezone` argument sets the time zone of times without one, and `reference` dates old logs without a year.
