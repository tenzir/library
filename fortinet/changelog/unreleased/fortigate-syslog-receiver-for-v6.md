---
title: FortiGate syslog receiver for v6
type: breaking
authors:
  - mavam
  - codex
prs:
  - 147
created: 2026-05-31T19:12:55Z
---

FortiGate syslog examples now use the v6 network source syntax.

Replace UDP syslog receivers that used the old source form with `accept_udp`
before parsing and mapping FortiGate logs:

```tql
from "udp://0.0.0.0:514" {
  read_syslog
}
fortinet::fortigate::ocsf::map
```

This keeps FortiGate onboarding pipelines compatible with the v6 executor.
