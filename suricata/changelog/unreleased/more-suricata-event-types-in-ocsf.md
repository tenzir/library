---
title: More Suricata event types in OCSF
type: feature
authors:
  - zedoraps
created: 2026-11-26T01:49:46.288396Z
---

More Suricata EVE event types map to OCSF:

- `rdp` events become RDP Activity with the negotiation steps, cookie, client details, and failure reasons.
- `ftp_data` events and FTP data files become FTP Activity.
- `mdns` events become DNS Activity.
- `arp`, `dcerpc`, `ldap`, `pop3`, `quic`, `rfb`, and `websocket` events become Network Activity. QUIC hellos add their JA3, JA3S, and JA4 fingerprints and the server name.
- HTTP/2 files become HTTP Activity, and HTTP/2 requests report their version.
