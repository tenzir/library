---
title: X-Forwarded-For addresses as intermediate IPs
type: change
authors:
  - zedoraps
created: 2026-11-18T13:32:14.770638Z
---

HTTP, file, and alert events now map the addresses in the X-Forwarded-For header to `src_endpoint.intermediate_ips`, in header order. The addresses come from `http.xff`, the raw header, or from `xff`, the address that Suricata's `xff` setting picks in `extra-data` mode. Detection Findings carry them in the source endpoint of their evidence. Mapped addresses no longer appear in `unmapped`. Clients control the header, so treat the addresses as claims. If an entry is no address, such as `unknown`, the other entries still map, and the raw header also stays in `unmapped.http.xff`. File events whose direction is unknown have no client endpoint and keep both fields in `unmapped`.

The mappings also drop the records that they leave without values, such as `unmapped.http: {}` and `unmapped.smtp: {}`, and omit `unmapped` when nothing remains.
