---
title: TLS fingerprints and server names on Suricata endpoints
type: change
authors:
  - zedoraps
created: 2026-11-18T11:43:10.728637Z
---

Suricata TLS events now expose the JA3 and JA3S fingerprints and the server name on the endpoints, so you can hunt for them like any other endpoint attribute:

- `src_endpoint.fingerprints` holds the client's JA3 and `dst_endpoint.fingerprints` the server's JA3S, as fingerprints with `algorithm_id: 99` (Other) and `algorithm` set to `JA3` or `JA3S`.
- `dst_endpoint.hostname` holds the SNI when it names a host. An SNI that is an IP address, with or without a port, stays in `tls.sni` only.

The `tls.ja3_hash`, `tls.ja3s_hash`, and `tls.sni` fields stay as before. For example, find all connections of a client fingerprint with:

```tql
where "37f463bf4616ecd445d4a1937da06e19" in src_endpoint.fingerprints?.map(x => x.value)
```

TLS events for which Suricata logged the version `UNDETERMINED`, which happens when it saw no negotiated version, such as for a lone ClientHello, no longer carry a `tls` object, because OCSF models a negotiated session there. They stay Network Activity events with the server name in `dst_endpoint.hostname`, and the version remains under `unmapped.tls.version`.
