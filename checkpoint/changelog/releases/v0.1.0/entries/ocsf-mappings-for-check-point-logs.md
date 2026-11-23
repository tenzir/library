---
title: OCSF mappings for Check Point gateway and management logs
type: feature
authors:
  - mavam
  - zedoraps
created: 2026-11-22T21:30:01Z
---

`checkpoint::ocsf::normalize` maps Check Point gateway and management records to OCSF 1.9:

- Firewall connections, including Encrypt and Decrypt VPN traffic and Application Control → Network Activity (4001), with NAT, zones, counters, and the deciding match-table rule.
- Records with a URL → HTTP Activity (4002), with method and URL categories.
- IPS, Anti-Bot, Anti-Malware, and other threat records → Detection Finding (2004), with the protection as analytic.
- DLP → Data Security Finding (2006), with the DLP incident and rule; MTA and Anti-Spam → Email Activity (4009).
- Log In, Log Out, and Failed Log In from management, Expert shell, Identity Awareness, Mobile Access, and remote access VPN → Authentication (3002), with the user group, ports, and client OS.
- Management API operations → API Activity (6003); SmartConsole and Web UI operations, policy installation, and publishing → Entity Management (3004).
- IKE Key Install → Tunnel Activity (4014).
- Other records, such as System Monitor and update notices → Base Event, with their fields in `unmapped`.

Check Point's severity (0 Informational to 4 Critical), confidence level, and application risk become `severity_id`, `confidence_id`, and `risk_level_id`; the session start and elapsed time become `start_time` and `duration`, aggregated logs give their window as `start_time`, `end_time`, and `count`, and the sent and received bytes and the client-side byte and packet counters become `traffic` in and out.

The action sets the security outcome: Detect is Observed; Prevent, Block, Drop, Reject, and Quarantine are Denied and a failed activity. The outcome of management operations and logins comes from `audit_status`.
