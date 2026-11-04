---
title: Preserved Zeek protocol context in OCSF
type: bugfix
prs:
  - 216
created: 2026-11-04T15:20:20.508587Z
---

Zeek mappings now include the required direction, device-type, and file-type classifications, using Unknown when the source does not report them. Optional DNS, HTTP, FTP, TLS, and device objects are constructed only when their required source values are available; unmapped facts keep their original source keys.

Native JSON records can omit optional connection, DNS, HTTP, and TLS fields, and SSH records no longer require optional direction, inference, or HASSH extensions. DNS answers remain strings when JSON parsing recognizes their values as IP addresses.

Standalone X.509 records become Base Events that retain the complete certificate record. RDP client names no longer imply a Windows desktop. SMTP observations without an email envelope retain their class and the corresponding OCSF validation warning.
