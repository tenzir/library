---
title: Harmony Endpoint and Harmony Email & Collaboration mappings
type: feature
authors:
  - zedoraps
created: 2026-11-23T10:00:00Z
---

The `checkpoint` package also maps Harmony Endpoint and Harmony Email & Collaboration events to OCSF 1.9:

```tql
checkpoint::email::parse
checkpoint::email::ocsf::normalize
```

- Harmony Endpoint events exported through Log Exporter go through the existing parsers and `checkpoint::ocsf::normalize`: Anti-Malware, Anti-Bot, Threat Emulation, Threat Extraction, Zero Phishing, Anti-Exploit, Anti-Ransomware, Behavioral Guard, and Forensics → Detection Finding (2004) with the file and its hashes; Anti-Malware scans → Scan Activity (6007); URL Filtering → HTTP Activity; Firewall and Application Control → Network Activity; DLP → Data Security Finding. The device is the endpoint computer with its OS, agent, and logged-on user as owner.
- Harmony Email & Collaboration security events from the events API or the SIEM JSON format → Detection Finding (2004), and DLP → Data Security Finding (2006), with the email, its attachments and links, the mailbox user, the state as finding status, and the latest remediation as outcome.
- Endpoint Compliance, Media Encryption & Port Protection, Full Disk Encryption, SSL Inspection, update, and quarantine restore records stay Base Events.
