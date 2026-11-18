---
title: Complete URLs for Zeek HTTP requests
type: change
authors:
  - zedoraps
created: 2026-11-18T15:21:57.567006Z
---

HTTP Activity events now carry the complete URL of a request in `http_request.url.url_string`, with `url.scheme` set to `http`, since Zeek only parses cleartext HTTP. For a request target in origin form, such as `/index.html`, the URL combines the scheme, the Host header, and the target. A port in the Host header, such as `203.176.135.102:8082`, now maps to `url.port` and no longer appears in `url.hostname`. The URL never takes the port of the connection. A proxy request in absolute form, such as `http://azenv.net/`, keeps the URL as sent and takes the scheme, host, port, path, and query from it, so its `url.path` no longer holds the whole URL. A request without a Host header keeps its path and query string but has no URL string. CONNECT targets, such as `example.org:443`, and other request targets that name no URL map no `url` object and stay in `unmapped.uri`.

Zeek logs `uri` percent-decoded, so `url_string` holds the decoded form.

```tql
where http_request.url.port? == 8082
```
