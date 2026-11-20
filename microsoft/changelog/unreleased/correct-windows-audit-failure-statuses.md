---
title: Correct Windows audit failure statuses
type: bugfix
authors:
  - zedoraps
created: 2026-11-20T19:07:22.647654Z
---

Windows Security events for SMB share access (5140 and 5145) and account mapping
(4774) now derive their OCSF status from the audit keyword bits. Denied operations
previously appeared as successful. Missing or ambiguous audit outcomes now map
to Unknown, and denied SMB access checks include their rendered access reasons
in `status_detail`.

Object handle requests (4656) use the same audit-bit handling. Conflicting
Winlogbeat audit labels preserve both bits, so these mappings report Unknown
instead of selecting an outcome based on label order.
