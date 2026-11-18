---
title: Decoded MIME attachment names
type: change
authors:
  - zedoraps
created: 2026-11-18T14:23:09.136241Z
---

Email Activity events from Suricata SMTP and `fileinfo` events now decode attachment names that the message encodes as a single Base64-encoded UTF-8 word (RFC 2047). For example, `email.files[].name` holds `66787196844.zip` instead of `=?UTF-8?B?NjY3ODcxOTY4NDQuemlw?=`. Names in other encodings or charsets, such as `=?UTF-8?Q?…?=` or `=?ISO-8859-1?B?…?=`, and names that consist of several encoded words stay as Suricata logged them.
