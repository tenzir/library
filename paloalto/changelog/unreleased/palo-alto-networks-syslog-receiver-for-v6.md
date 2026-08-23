---
title: Palo Alto Networks syslog receiver for v6
type: breaking
authors:
  - mavam
  - codex
prs:
  - 147
created: 2026-05-31T19:12:55Z
---

The Palo Alto Networks package now parses PAN-OS CSV payloads with positional
input and output fields. It also maps PAN-OS Traffic, URL Filtering,
Threat, and supported GlobalProtect authentication records to OCSF 1.9. Other
parsed families become OCSF Base Events and retain their structured fields in
`unmapped`.

Normalize a Syslog record in one call:

```tql
accept_udp "udp://0.0.0.0:514"
this = data.parse_syslog()
paloalto::ocsf::normalize
```

Use `paloalto::parse` and `paloalto::ocsf::map` separately when a pipeline needs
to inspect or enrich the parsed PAN-OS record before mapping.
