---
title: Check Point Log Exporter parsing
type: feature
authors:
  - mavam
  - zedoraps
created: 2026-11-22T21:30:00Z
---

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
