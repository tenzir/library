---
title: Add Cisco Secure Firewall ASA support
type: feature
authors:
  - zedoraps
created: 2026-06-18T00:00:00Z
---

The `cisco` package now parses Cisco Secure Firewall ASA syslog messages and
maps supported message IDs to OCSF.

`cisco::asa::parse` extracts the `%ASA-<severity>-<message_id>: <text>` frame
from a message field and parses the body of supported messages into structured
fields. It takes a `message` argument naming the field that holds the raw line
(default `content`, as produced by the built-in `read_syslog`), so it composes
with any transport:

```tql
from_tcp "0.0.0.0:514" {
  read_syslog
}
cisco::asa::parse message="content"
cisco::asa::ocsf::map
ocsf::derive
ocsf::cast
```

Point `message` at another field for other delivery methods, e.g.
`message="line"` after `read_lines`, or the body field a log shipper uses.

`cisco::asa::ocsf::map` maps connection-built (302013/302015), connection-
teardown (302014/302016), and access-list deny (106023) messages to OCSF
Network Activity events. Unsupported messages map to the OCSF Base Event and
retain their original text.
