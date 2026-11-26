---
title: More faithful Suricata activities and files
type: bugfix
authors:
  - zedoraps
created: 2026-11-26T01:49:47.145043Z
---

Several Suricata events map more faithfully to OCSF:

- SNMP and SIP messages are traffic and state their initiator; SIP no longer opens, closes, or fails connections.
- FTP and SMB commands that OCSF lists no activity for use activity Other with the command as name.
- Alerts no longer put the generator ID into `finding_info.analytic.algorithm`.
- Failed SMB creates no longer report a file size of 0.
- HTTP/2 control frames become Network Activity instead of HTTP Activity without a request.
- HPACK table size updates no longer appear as HTTP headers.
- HTTP bodies that Suricata names after the URL path keep their hashes in `file`.
