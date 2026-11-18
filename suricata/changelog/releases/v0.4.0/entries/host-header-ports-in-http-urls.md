---
title: Host header ports in HTTP URLs
type: change
authors:
  - zedoraps
created: 2026-11-18T14:20:50.55052Z
---

HTTP, file, and alert events now map the port that the client wrote in the Host header, Suricata's `http.http_port`, to `http_request.url.port`, and include it in `http_request.url.url_string`. For example, a request with `Host: 203.176.135.102:8082` has the URL `http://203.176.135.102:8082/ono32/…` instead of `http://203.176.135.102/ono32/…`. Without a port in the Host header, the URL has no port, even when the connection uses a non-standard one. Suricata logs port 0 for requests without a host, which stays in `unmapped.http.http_port`.
