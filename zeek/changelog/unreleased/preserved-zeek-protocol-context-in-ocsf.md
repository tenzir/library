---
title: Preserved Zeek protocol context in OCSF
type: bugfix
prs:
  - 216
created: 2026-11-04T15:20:20.508587Z
---

Zeek mappings now include the required direction, device-type, and file-type classifications, using Unknown when the source does not report them. Optional DNS, HTTP, FTP, TLS, and device objects are constructed only when their required source values are available; unmapped facts keep their original source keys.

Native JSON records can omit optional connection, DNS, HTTP, and TLS fields, and SSH records no longer require optional direction, inference, or HASSH extensions. DNS answers, HTTP host names, and TLS server names remain strings when JSON parsing recognizes their values as IP addresses. SMB file timestamps from native JSON are converted from Unix seconds. FTP records without replies or data-channel metadata no longer imply an active data channel, and unused data-channel facts keep their original keys. Unassigned and reserved DNS response codes use the corresponding OCSF classifications while preserving the original wire codes. DNS events retain their connection identifiers and transport protocol. Unknown RDP results retain their source text without lookup warnings.

Standalone X.509 records become Base Events that retain the complete certificate record. RDP client names no longer imply a Windows desktop. SMTP negotiation without an email envelope or message content becomes Network Activity traffic tagged with the SMTP application protocol, retaining the original negotiation fields. Observed email envelopes and partial messages remain Email Activity events.
