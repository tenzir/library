---
title: Zeek TLS fingerprints and server names on endpoints
type: change
authors:
  - zedoraps
created: 2026-11-18T11:42:42.452371Z
---

Zeek TLS records whose handshake never finished no longer produce an invalid OCSF `tls` object, and every TLS record now exposes its JA3 and JA3S fingerprints and its SNI on the endpoints. Zeek logs no TLS version when it saw no ServerHello, for example when the client sent only a ClientHello or the server answered only with an alert. These records previously carried a `tls` object without the `version` that OCSF requires. They now stay Network Activity events without a `tls` object, and facts without an OCSF counterpart, such as `ssl_history`, remain under `unmapped`.

For all TLS records, whether the handshake finished or not:

- `src_endpoint.fingerprints` holds the client's JA3 and `dst_endpoint.fingerprints` the server's JA3S, as fingerprints with `algorithm_id: 99` (Other) and `algorithm` set to `JA3` or `JA3S`.
- `dst_endpoint.hostname` holds the SNI when it names a host. An SNI that is an IP address, with or without a port, stays in `tls.sni`, or under `unmapped.server_name` when there is no `tls` object.
- `status_code` holds the numeric TLS alert code next to the alert name in `status_detail`.

Completed handshakes keep `tls.ja3_hash`, `tls.ja3s_hash`, and `tls.sni`. Failed handshakes often come from malware, so you can now hunt for a client fingerprint or a server name across all TLS records, for example:

```tql
where "37f463bf4616ecd445d4a1937da06e19" in src_endpoint.fingerprints?.map(x => x.value)
```
