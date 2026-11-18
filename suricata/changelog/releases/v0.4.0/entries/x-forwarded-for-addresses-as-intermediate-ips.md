---
title: X-Forwarded-For addresses as intermediate IPs
type: change
authors:
  - zedoraps
created: 2026-11-18T13:32:14.770638Z
---

HTTP, file, and alert events now map the addresses in the X-Forwarded-For header to `src_endpoint.intermediate_ips`, in header order. The addresses come from `http.xff`, the raw header, or from `xff`, the address that Suricata's `xff` setting picks in `extra-data` mode. Detection Findings carry them in the source endpoint of their evidence. Clients control the header, so treat the addresses as claims. If an entry is no address, such as `unknown`, the other entries still map. The header itself joins `http_request.http_headers` as `X-Forwarded-For`, unless extended logging already lists it in `http.request_headers`, so its value survives even when no entry is an address, and `http.xff` and `xff` no longer appear in `unmapped`. File events whose direction is unknown have no client endpoint, so they carry the header but no intermediate IPs.

The mappings also drop the records that they leave without values, such as `unmapped.http: {}` and `unmapped.smtp: {}`. `unmapped` itself stays, even when nothing remains.

The null fields that `read_suricata` adds for every EVE field a record lacks also leave `unmapped`, and `connection_info.tcp_flags` and `tls.certificate.sans` are only set when Suricata logs them.
