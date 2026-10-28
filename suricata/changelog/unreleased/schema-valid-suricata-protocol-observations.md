---
title: Schema-valid Suricata protocol observations
type: bugfix
authors:
  - zedoraps
created: 2026-10-28T11:20:39.371008Z
prs:
  - 208
  - 205
---

Suricata normalization now retains native DNS SOA data, SMTP addresses, and SMB file timestamps in their OCSF representations. Incomplete DNS records, HTTP responses, certificates, hashes, and identities remain in unmapped data. Observations missing identities required by their activity class become Base Events with their original mapping preserved.
