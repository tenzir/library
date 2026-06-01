---
title: Palo Alto Networks syslog receiver for v6
type: breaking
authors:
  - mavam
  - codex
prs:
  - 147
created: 2026-05-31T19:12:55Z
---

Palo Alto Networks syslog examples now use the v6 network source syntax and the
new PAN-OS CSV parser.

Receive UDP syslog with `accept_udp`, parse the payload with
`paloalto::parse`, and then continue with your routing or mapping workflow:

```tql
from "udp://0.0.0.0:514" {
  read_syslog
}
paloalto::parse
```
