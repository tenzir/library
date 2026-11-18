---
title: Zeek SMTP envelope addresses in Email Activity
type: breaking
authors:
  - zedoraps
created: 2026-11-18T09:56:02.902381Z
---

Zeek SMTP records with an SMTP envelope but no message headers now produce valid OCSF Email Activity events. Zeek logs the header `From` and `To` addresses only once the client transmits the message, so transactions that ended earlier, most often because the server rejected the sender or a recipient, previously produced Email Activity events without the `from` or `to` address that the `email` object requires.

The `email.from` and `email.to` fields now take the header addresses and fall back to the envelope sender (`MAIL FROM`) and recipients (`RCPT TO`). The `email.from_mailbox`, `email.to_mailboxes`, and `email.cc_mailboxes` fields hold header values only, so an empty `from_mailbox` tells that `from` came from the envelope. For example, find rejected envelopes with:

```tql
where class_uid == 4009 and email.from_mailbox? == null and status_id == 2
```

The envelope itself moves from the deprecated `email.smtp_from` and `email.smtp_to` fields to `email.return_path` and `email.delivered_to_list`, which always hold the envelope sender and recipients. Zeek SMTP events no longer set `email.smtp_from` or `email.smtp_to`, so queries that read them need to switch to the new fields.

Email Activity events also leave two more deprecated attributes behind. The address from the `Reply-To` header moves from `email.reply_to` to the list `email.reply_to_list`, next to the unchanged `email.reply_to_mailboxes`. The HELO/EHLO argument, the host name that the client reports for itself, moves from `smtp_hello` to the class attribute `command`:

```tql
// Before
where smtp_hello == "localhost"
// After
where class_uid == 4009 and command == "localhost"
```

`command` holds only the argument, because Zeek doesn't log whether the client sent HELO or EHLO.

Records without an envelope or header addresses, such as an SMTP negotiation alone, become OCSF Network Activity with `app_protocol_name: "smtp"` and keep partial message details, such as `helo` and `subject`, under `unmapped`.

All SMTP records now take `status`, `status_code`, and `status_detail` from Zeek's `last_reply`. The class of the reply code decides: 2xx is a success, 4xx and 5xx a failure, and a 3xx reply such as `354` after `DATA` leaves the transaction unfinished, so its status is unknown. Both classes now map the hosts from Zeek's `path` that handed on the message before it reached the client to `src_endpoint.intermediate_ips`, instead of placing the whole path, including the connection's own server and client, in the `dst_endpoint.intermediate_ips` of Email Activity events.

Header lists distinguish known from unknown absence: when Zeek saw the message headers, a missing `To`, `Cc`, or `Reply-To` header yields an empty list, and without any headers, such as after a rejected envelope, these lists stay null.
