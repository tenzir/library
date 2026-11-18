---
title: Zeek proxy headers as HTTP request headers
type: change
authors:
  - zedoraps
created: 2026-11-18T15:09:50.274234Z
---

HTTP Activity events now map the proxy headers that Zeek logs in `proxied`, such as `X-FORWARDED-FOR`, `VIA`, and `FORWARDED`, to `http_request.http_headers`, after the headers from `client_headers`. A header that `client_headers` already lists with the same value does not repeat. The addresses in X-Forwarded-For map to `src_endpoint.intermediate_ips`, in header order. Clients control the header, so treat the addresses as claims. Entries that are no address, such as `unknown` or a Log4Shell probe, only stay in the header. `proxied` no longer appears in `unmapped`.

```tql
where 137.135.117.126 in src_endpoint.intermediate_ips?
```
