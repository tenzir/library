---
title: SMTP envelope addresses in Email Activity
type: change
authors:
  - zedoraps
created: 2026-11-18T10:12:11.500363Z
---

SMTP events with an SMTP envelope but no parsed message headers now produce valid OCSF Email Activity events. Suricata logs the header `From` and `To` addresses only when its MIME parser found them, so rejected, interrupted, or incompletely parsed messages previously produced Email Activity events without the `from` or `to` address that the `email` object requires.

The `email.from` and `email.to` fields now take the header addresses and fall back to the envelope sender (`MAIL FROM`) and recipients (`RCPT TO`). The `email.from_mailbox`, `email.to_mailboxes`, and `email.cc_mailboxes` fields hold header values only, so an empty `from_mailbox` tells that `from` came from the envelope. For example, find messages without a parsed header sender with:

```tql
where class_uid == 4009 and email.from_mailbox? == null
```

The envelope itself moves from the deprecated `email.smtp_from` and `email.smtp_to` fields to `email.return_path` and `email.delivered_to_list`, which always hold the envelope sender and recipients. Suricata SMTP and `fileinfo` events no longer set `email.smtp_from` or `email.smtp_to`, so queries that read them need to switch to the new fields.

Plain HELO and STARTTLS sessions without an envelope or header addresses map to Network Activity traffic tagged with the SMTP application protocol, with their HELO name under `unmapped`.
