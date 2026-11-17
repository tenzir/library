This release corrects how the Suricata package maps DNS, SMB, SMTP, Kerberos, FTP, HTTP, TLS, MQTT, and flow events to OCSF 1.9.0, including events that read_suricata parses with null-filled schemas.

## 🐞 Bug fixes

### Accurate OCSF semantics for Suricata events

Several Suricata mappings put source fields into OCSF attributes with a different meaning, or lost them when events came from `read_suricata`. They now map as follows:

- DNS events from EVE version 2 map the question to `query`, queries to the Query activity, and the `SERVFAIL` and `FORMERR` response codes to their OCSF identifiers. Queries no longer report a failed status, a response code, or all six header flags, and the AD and CD flags come from the raw header. Answers in the grouped format land in `answers`, and additional records belong to the query or the response that carried them.
- SMB events name the UNC share in `share` with its type, and the file within it in `file.name` and `file.path`, with its size, ID, and folder type. The access mode lands in `open_type`. NTLMSSP session setups report the account in `actor.user` and the client host name, and the operating systems of client and server land in their endpoints instead of `device`. Events without a status and session setups that need more processing report an unknown status instead of a failure, and SMB timestamps use seconds.
- SMTP envelope senders and recipients land in `email.smtp_from` and `email.smtp_to` without angle brackets. The `email.from`, `email.to`, and `email.cc` fields hold the header addresses next to their human-readable mailboxes, and messages expose their subject, attachments, and URLs. Messages use the Send activity, and the parser state no longer implies a successful delivery. SMTP negotiation without any message becomes Network Activity traffic tagged with the SMTP application protocol.
- Kerberos requests report an unknown status instead of a failure, and clients become the source endpoint when Suricata logs a TCP transaction in the reply direction. Weak encryption no longer claims cleartext credentials, and errors keep the failed request type under `unmapped`.
- FTP events describe a file only for commands that take one, report the `USER` name in `actor.user`, and take the status from the last reply code.
- HTTP events map WebDAV methods to their activities and create a request or response only when Suricata observed one.
- TLS events keep the observed JA3 fingerprints and server name, and no longer report `Unknown` when Suricata logged no version.
- MQTT events tag the application protocol, and CONNACK failures report a failed connection. Messages without an outcome report an unknown status instead of success.
- Connections over ICMPv6 and SCTP carry their IANA protocol numbers, and unknown protocols no longer claim number 0. Events without addresses carry no connection, and endpoints take address and port from the same source.
- DHCP events no longer replace the client address with `0.0.0.0`, file events use the Regular File type, and NetFlow records map their byte and packet counts.

Validation continues to report actors, users, and email header addresses that the sensor did not observe.

*By @zedoraps in #217.*
