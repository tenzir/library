---
title: Preserved Suricata protocol observations
type: bugfix
authors:
  - zedoraps
created: 2026-10-28T11:20:39.371008Z
prs:
  - 208
  - 205
---

Suricata mappings retain native DNS SOA data, SMTP addresses, and SMB file timestamps in their OCSF representations. Known protocol observations keep their class and activity when required context is missing, with OCSF validation reporting warnings. Unsupported event types use an explicit Base Event mapping and retain their source fields.
