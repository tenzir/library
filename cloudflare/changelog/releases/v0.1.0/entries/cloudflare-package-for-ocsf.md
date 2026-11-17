---
title: Cloudflare package for OCSF
type: feature
authors:
  - mavam
prs:
  - 240
created: 2026-11-17T08:50:18.225217Z
---

The library now includes a `cloudflare` package that maps Cloudflare Logpush data to OCSF 1.9.0.

| Logpush dataset   | OCSF class                                             |
| ----------------- | ------------------------------------------------------ |
| `http_requests`   | HTTP Activity, with the Network Proxy profile          |
| `firewall_events` | HTTP Activity, with the Security Control profile       |
| `audit_logs_v2`   | API Activity, with the Cloud profile                   |

Tenzir reads Logpush's newline-delimited JSON natively, so you only need the normalizer between your source and your destination:

```tql
from_file "s3://example-logpush/http_requests/**/*.log.gz", watch=1min {
  decompress_gzip
  read_ndjson
}
cloudflare::ocsf::normalize dataset="http_requests"
to_hydrolix "https://hydrolix.example.com",
  table="security.ocsf",
  token=secret("HYDROLIX_TOKEN")
```

The client becomes the source endpoint, the Cloudflare data center the proxy endpoint, and the origin the destination endpoint. Client TLS and JA3/JA4 fingerprints, WAF and custom rule matches with their actions, and the Ray ID that correlates a request with its firewall events all map to OCSF. Bot and WAF attack scores stay under `unmapped` with their Cloudflare names.

`cloudflare::audit_logs::fetch` pulls account audit logs from the Cloudflare API in the Logpush layout, so the same normalizer maps them:

```tql
cloudflare::audit_logs::fetch "023e105f4ecef8ad9ca31a8372d0c353",
  api_token=secret("CLOUDFLARE_API_TOKEN"),
  since=now() - 1d
cloudflare::ocsf::normalize
to_splunk "https://splunk.example.com:8088",
  hec_token=secret("SPLUNK_HEC_TOKEN"),
  index="cloudflare"
```
