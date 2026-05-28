# Check Point Fixture Matrix

The samples in this directory are sanitized fixtures for parser and OCSF mapper
tests. The `checkpoint.ndjson` firewall records are local sanitized firewall
traffic samples. The expanded records use documented Log Exporter field names
from public references, especially the LogRhythm Check Point Log Exporter V2.0
parser catalog and the Check Point Log Exporter administration guide.

| Fixture | Source or Provenance | Exporter Format | Product or Blade | Discriminator | Canonical `@name` | Expected OCSF |
| --- | --- | --- | --- | --- | --- | --- |
| `checkpoint-syslog-structured-data.log` | Local sanitized RFC5424 sample | Syslog structured data | VPN-1 & FireWall-1 | `action=Accept` | `checkpoint.firewall.network` | Network Activity |
| `checkpoint-syslog-kv-message.log` | Local sanitized RFC5424 sample | Pipe-delimited KV message | Firewall | `action=Drop` | `checkpoint.firewall.network` | Network Activity |
| `checkpoint.ndjson` accept | Local sanitized JSON export | JSON/NDJSON | VPN-1 & FireWall-1 | `action=Accept` | `checkpoint.firewall.network` | Network Activity |
| `checkpoint.ndjson` drop | Local sanitized JSON export | JSON/NDJSON | VPN-1 & FireWall-1 | `action=Drop` | `checkpoint.firewall.network` | Network Activity |
| `checkpoint.ndjson` detect | Local sanitized JSON export | JSON/NDJSON | VPN-1 & FireWall-1 | `message_info=Address spoofing` | `checkpoint.firewall.threat` | Detection Finding |
| `checkpoint.ndjson` reject | Local sanitized JSON export | JSON/NDJSON | VPN-1 & FireWall-1 | `action=Reject` | `checkpoint.firewall.network` | Network Activity |
| `checkpoint-expanded.ndjson` `net-nat-1` | Synthetic from documented core/VPN-1 fields | JSON/NDJSON | VPN-1 & FireWall-1 | NAT, bytes, packets, zones | `checkpoint.firewall.network` | Network Activity |
| `checkpoint-expanded.ndjson` `url-1` | Synthetic from documented Application Control/URL Filtering fields | JSON/NDJSON | URL Filtering | URL and application fields | `checkpoint.firewall.web_resource` | Web Resource Access Activity |
| `checkpoint-expanded.ndjson` `threat-1` | Synthetic from documented IPS/threat-prevention fields | JSON/NDJSON | IPS | `threatname` and `protection_name` | `checkpoint.firewall.threat` | Detection Finding |
| `checkpoint-expanded.ndjson` `dlp-1` | Synthetic from documented DLP fields | JSON/NDJSON | DLP | `data_type`, `object`, sender/recipient | `checkpoint.firewall.dlp` | Data Security Finding |
| `checkpoint-expanded.ndjson` `vpn-1` | Synthetic from documented Mobile Access/Connectra fields | JSON/NDJSON | Mobile Access | VPN session and user fields | `checkpoint.firewall.vpn` | Tunnel Activity |
| `checkpoint-expanded.ndjson` `email-1` | Synthetic from documented MTA/Anti-Spam fields | JSON/NDJSON | MTA | sender, recipient, subject | `checkpoint.firewall.email` | Email Activity |
| `checkpoint-expanded.ndjson` `api-1` | Synthetic from documented WEB_API fields | JSON/NDJSON | WEB_API | API action and object fields | `checkpoint.management.api` | API Activity |
| `checkpoint-expanded.ndjson` `audit-1` | Synthetic from documented SmartConsole/Web UI fields | JSON/NDJSON | SmartConsole | management action and object fields | `checkpoint.management.audit` | Entity Management |

References:

- https://sc1.checkpoint.com/documents/Log_Exporter/EN/Content/Topics/Introduction.htm
- https://sc1.checkpoint.com/documents/Log_Exporter/EN/CP_Log_Exporter_AdminGuide.pdf
- https://docs.logrhythm.com/devices/docs/syslog-check-point-log-exporter-v2-0
- https://www.elastic.co/docs/reference/beats/filebeat/filebeat-module-checkpoint
