---
title: Accurate OCSF semantics for Zeek protocol logs
type: bugfix
authors:
  - zedoraps
prs:
  - 216
created: 2026-11-04T15:20:20.508587Z
---

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
