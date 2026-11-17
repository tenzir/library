This release corrects how the Zeek package maps SMTP, SMB, HTTP, FTP, DNS, TLS, and RDP fields to OCSF 1.9.0, keeps observed facts when native JSON omits optional fields, and records standalone certificates as Base Events. Zeek notices, weirds, and analyzer violations now map to Detection Finding and Network Activity.

## 🚀 Features

### OCSF mappings for Zeek notices, weirds, and analyzer violations

Zeek's own detections from `notice.log` become OCSF Detection Findings. Each finding carries the notice type as its title and analytic, the message as its description, the endpoints and transferred files as evidence, and the MITRE ATT&CK techniques that ATT&CK notices list.

Protocol anomalies from `weird.log` and analyzer violations from `analyzer.log` become Network Activity events with their endpoints and the anomaly or violation text as `message`, so you can find them by IP address and port like other connection events. Records without a connection stay Base Events.

*By @zedoraps.*

## 🐞 Bug fixes

### Accurate OCSF semantics for Zeek protocol logs

Several Zeek mappings put source fields into OCSF attributes with a different meaning. They now map as follows:

- SMTP envelope senders and recipients land in `email.smtp_from` and `email.smtp_to`. The `email.from`, `email.to`, and `email.cc` fields hold the header addresses next to their human-readable mailboxes. The HELO host name lands in `smtp_hello` instead of `command`, and the last reply code determines the status, so rejected deliveries show up as failures.
- SMB events name the UNC share in `share`, and the file within it in `file.name` and `file.path`. The share root becomes a folder and named pipes become pipes.
- HTTP events keep the method token, such as `POST`, split the query string from the URL path, and derive the status from the response code.
- FTP events describe a file only for commands that take one, with the URL, MIME type, and file ID of transfers. Reply codes determine the status.
- DNS events use the round-trip time for `response_time`, and DNS and HTTP events report an unknown direction instead of Other. Unassigned and reserved response codes use the OCSF range identifiers and keep the original wire code.
- TLS events keep the observed JA3 fingerprints and server name when the handshake ended before a version was negotiated.
- RDP events take the status from Corelight's `auth_success` when the result is encrypted, and client names no longer imply a Windows desktop.

Zeek logs without a dedicated mapping keep their log name, such as `files.log`, when a Zeek reader provides it. Standalone X.509 records become Base Events that retain the complete certificate record. SMTP negotiation without any message becomes Network Activity traffic tagged with the SMTP application protocol.

Records from native Zeek JSON can omit optional fields. Text values that JSON parsing infers as IP addresses stay strings, and Unix-second timestamps and durations become time values. Source fields that Zeek left unset no longer appear as null values under `unmapped`.

*By @zedoraps in #216.*

### Zeek normalization without `type_of` deprecation warnings

The Zeek OCSF mapping no longer emits `type_of` deprecation warnings on Tenzir v6.20. It now detects time and floating-point `ts` values with the `type_kind` function, and still maps both to the OCSF `time` field.

Native connection durations, DHCP lease durations, DNS TTLs, and unsigned response codes are also normalized without conversion warnings.

*By @IyeOnline in #200.*
