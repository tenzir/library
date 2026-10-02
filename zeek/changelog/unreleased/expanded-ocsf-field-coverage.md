---
title: Expanded OCSF 1.9 field coverage
type: change
authors:
  - mavam
prs:
  - 191
created: 2026-10-02T14:34:36.176888Z
---

Zeek OCSF events now expose DNS transaction IDs and flags, HTTP body lengths and usernames, FTP users, SMTP URLs, connection intervals and VLAN IDs, SMB file attributes, SSH version/status, and network-observer identity. Represented aliases are consumed while unsupported protocol details remain in `unmapped`.
