---
title: Add Cisco Secure Firewall ASA support
type: feature
authors:
  - zedoraps
created: 2026-06-18T00:00:00Z
---

The `cisco` package now parses Cisco Secure Firewall ASA syslog messages and
maps them to OCSF.

`cisco::asa::parse` extracts the `%ASA-<severity>-<message_id>: <text>` frame
from a field and parses the body of supported messages into structured fields.
It takes a `message` field argument (default `content`, as produced by the
built-in `read_syslog`), so it composes with any transport:

```tql
from_tcp "0.0.0.0:514" {
  read_syslog
}
cisco::asa::parse
cisco::asa::ocsf::map
ocsf::derive
ocsf::cast
```

Point `message` at another field for other delivery methods, e.g. `message=line`
after `read_lines`, or the body field a log shipper provides.

`cisco::asa::ocsf::map` maps the common firewall messages by ID:

- **OCSF Network Activity (4001)**: connection setup and teardown
  (302013/302015, 302014/302016/302021); access-list, protocol, and ICMP denies
  plus access-list hit-count logs (106001, 106006/106007, 106010, 106014,
  106023, 106100, 313004/313008, 710003/710005); and duplicate TCP SYN (419002).
- **OCSF Authentication (3002)**: VPN session logon and logoff and
  identity-mapping changes (722051, 113019, 746013).

Every other message maps to the OCSF Base Event with its original text
preserved. The ASA message ID is recorded in `metadata.event_code`, and the
reporting host in `metadata.loggers`.
