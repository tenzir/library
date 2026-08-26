---
title: Correlated OpenSSH normalization
type: feature
created: 2026-08-22T00:00:00Z
---

`openssh::ocsf::normalize` now uses the complete Syslog record for OCSF
`raw_data` when `read_syslog` retains that record in the `raw` field.

The new optional `openssh::aggregate` operator correlates adjacent OpenSSH
records from the same host, process, and event phase. It combines accepted
logins with PAM session details, invalid-user attempts with their
pre-authentication close, and disconnect records with their reason.
Correlated OCSF events retain every source record and carry aggregate timing and
count fields.

The normalizer reads the RFC 5424 `message` and timestamp fields. For classic
RFC 3164 files such as `/var/log/auth.log`, adapt the Syslog envelope first:

```tql
from_file "/var/log/auth.log" {
  read_syslog raw_message=raw
}
where app_name in openssh::$app_names
message = move content
timestamp = timestamp.parse_time("%b %e %H:%M:%S", reference=now())
openssh::ocsf::normalize
```

The parser now handles PAM authentication failures, postponed authentication,
extra whitespace in invalid-user messages, anonymous connection closes,
connection resets, and connection timeouts. Anonymous closes and transport
errors map to OCSF Network Activity instead of status-less Authentication
events.

The raw fixtures cover Alpine Linux, Arch Linux, Debian, openSUSE Leap, Red Hat
UBI, and Ubuntu. They include successful and failed password,
keyboard-interactive, ED25519, ECDSA, RSA, and certificate authentication. They
also include the `publickey,password`, `publickey,keyboard-interactive`, and
`publickey,publickey` policies, PAM account locking, and OpenSSH's built-in
per-source connection penalties.

The generated fixtures do not cover GSSAPI, host-based, or FIDO authentication.
Those methods require Kerberos, host trust, or a hardware-backed authenticator.

The aggregator recognizes OpenSSH's `Partial` records and preserves every
completed factor in multi-step authentication events. It also combines a
certificate validation error with the matching failed public-key event.

The mapper maps Syslog metadata, host information, authentication factors,
credentials, certificates, session details, endpoints, and human-readable
event messages. If `raw` is absent, it uses the OpenSSH message body. For a
correlated event, its OCSF severity reflects the most severe constituent
Syslog record.

Authentication methods now map to OCSF authentication factors. Standalone
postponed attempts map to Preauth, SSH logons use the Network logon type, and
server-side connection records use the Inbound direction. Authentication,
transport, forwarding, and daemon lifecycle messages map to their matching
OCSF classes. Events without enough context for a specific class remain Base
Events.
