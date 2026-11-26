---
title: HarfangLab HEC envelopes from the OCSF export
type: feature
authors:
  - zedoraps
prs:
  - 278
created: 2026-11-26T22:03:09.506604Z
---

`harfanglab::fetch` takes a new `envelope` option. With `format="ocsf"` and
`envelope=true`, it returns the Splunk export's HEC envelopes unchanged instead
of the OCSF events alone:

```tql
harfanglab::fetch "https://example.hurukai.io:8443",
  token=secret("harfanglab-api-token"),
  envelope=true
```

The envelope's `sourcetype`, such as `harfanglab:raw_socket_creation`, names
HarfangLab's log type, which the OCSF class doesn't always reveal. Use it to
archive the export exactly as the Manager sends it.

The ECS reduction example now sends the reduced stream to Elasticsearch.
