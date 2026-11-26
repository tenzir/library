---
title: More Windows events in fitting OCSF classes
type: feature
authors:
  - zedoraps
created: 2026-11-26T02:48:28.98773Z
---

More Windows events map to fitting OCSF classes:

- Windows Filtering Platform connections 5156 and 5157 to Network Activity, with the remote peer of an inbound connection as the source.
- Remote Desktop Services user authentication 1149 and session logons and logoffs 21 and 23 to Authentication, and session disconnects and reconnects 24 and 25 to RDP Activity.
- Services that fail to start 7000 to Application Lifecycle, and task actions that fail to launch 203 to Scheduled Job Activity.
- Microsoft Defender Antivirus scans 1000, 1001, and 1002 to Scan Activity.
- BITS URL transfers 59, 60, and 61 to HTTP Activity.
