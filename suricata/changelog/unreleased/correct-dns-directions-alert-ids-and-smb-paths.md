---
title: Correct DNS directions, alert IDs, and SMB paths
type: bugfix
authors:
  - zedoraps
created: 2026-11-25T23:30:11.67707Z
---

DNS, alert, and SMB events map more faithfully to OCSF:

- DNS requests no longer report a response code or a success status.
- DNS responses put the client into `src_endpoint` and the server into `dst_endpoint`.
- Each alert gets its own `finding_info.uid`; the signature ID remains in `finding_info.analytic.uid`.
- SMB file paths keep the path as Suricata logs it when the share is unknown, without a leading backslash.
- SMB events no longer report an empty share or file ID, or a session or tree ID of 0.
