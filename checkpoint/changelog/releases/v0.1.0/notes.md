The Check Point package parses Log Exporter records from syslog and JSON exports exactly as the gateway writes them and maps gateway and management records to OCSF 1.9, from firewall traffic with its byte counters to logins, management operations, and threat findings. It also maps Harmony Endpoint and Harmony Email & Collaboration events.

## 🚀 Features

### Check Point Log Exporter parsing

The `checkpoint` package parses Check Point Log Exporter records from syslog and JSON exports:

```tql
accept_udp "0.0.0.0:514"
this = data.parse_syslog(raw=true)
checkpoint::syslog::parse_structured_data
checkpoint::ocsf::normalize
```

- `checkpoint::syslog::parse_structured_data` reads structured data, with `sd_id="Fields@1.3.6.1.4.1.2620"` for the RFC 5424 key=value form; `parse_kv_message` and `parse_kv_content` read pipe-delimited RFC 5424 messages and RFC 3164 content.
- `checkpoint::parse` normalizes JSON exports and the extracted fields: alternative field names, epoch seconds, epoch milliseconds, and ISO 8601 times, IP addresses, ports, counters, NAT translations, and match-table fields.
- SecureXL packet tuple samples in `packets` and every match-table entry stay available.

*By @mavam and @zedoraps.*

### Harmony Endpoint and Harmony Email & Collaboration mappings

The `checkpoint` package also maps Harmony Endpoint and Harmony Email & Collaboration events to OCSF 1.9:

```tql
checkpoint::email::parse
checkpoint::email::ocsf::normalize
```

- Harmony Endpoint events exported through Log Exporter go through the existing parsers and `checkpoint::ocsf::normalize`: Anti-Malware, Anti-Bot, Threat Emulation, Threat Extraction, Zero Phishing, Anti-Exploit, Anti-Ransomware, Behavioral Guard, and Forensics → Detection Finding (2004) with the file and its hashes; Anti-Malware scans → Scan Activity (6007); URL Filtering → HTTP Activity; Firewall and Application Control → Network Activity; DLP → Data Security Finding. The device is the endpoint computer with its OS, agent, and logged-on user as owner.
- Harmony Email & Collaboration security events from the events API or the SIEM JSON format → Detection Finding (2004), and DLP → Data Security Finding (2006), with the email, its attachments and links, the mailbox user, the state as finding status, and the latest remediation as outcome.
- Endpoint Compliance, Media Encryption & Port Protection, Full Disk Encryption, SSL Inspection, update, and quarantine restore records stay Base Events.

*By @zedoraps.*

### OCSF mappings for Check Point gateway and management logs

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

*By @mavam and @zedoraps.*
