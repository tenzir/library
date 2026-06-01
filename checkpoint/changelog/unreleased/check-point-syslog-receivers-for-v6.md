---
title: Check Point syslog receivers for v6
type: breaking
authors:
  - mavam
  - codex
prs:
  - 147
created: 2026-05-31T19:12:55Z
---

Check Point syslog examples now use the v6 network source syntax.

Replace UDP syslog receivers that used the old source form with `accept_udp`:

```tql
from "udp://0.0.0.0:514" {
  read_syslog
}
checkpoint::syslog::parse_structured_data
checkpoint::ocsf::map
```

This keeps the Check Point onboarding examples compatible with the v6 executor.
