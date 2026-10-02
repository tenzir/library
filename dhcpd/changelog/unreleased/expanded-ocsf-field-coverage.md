---
title: Expanded OCSF 1.9 field coverage
type: change
authors:
  - mavam
prs:
  - 191
created: 2026-10-02T14:34:35.378627Z
---

DHCPD OCSF events now expose a supplied server hostname as `device.hostname`. Relay display values are consumed only when they duplicate the mapped relay IP or interface; DHCPv6 and parser-specific context remains in `unmapped`.
