---
title: Source-aware firewall observation context
type: bugfix
authors:
  - zedoraps
created: 2026-10-28T11:20:37.695418Z
prs:
  - 208
---

PAN-OS mappings now construct optional locations, endpoint owners, NAT proxies, firewall rules, policies, and evidence users from the corresponding source identities. Unused facts, including human-readable country names, retain their original source keys in `unmapped`.
