---
title: HarfangLab package
type: feature
authors:
  - zedoraps
created: 2026-11-26T15:00:00Z
---

The library now includes a `harfanglab` package that fetches events from a
[HarfangLab](https://harfanglab.io/) Manager through its pull exports:

```tql
harfanglab::fetch "https://example.hurukai.io:8443",
  token=secret("harfanglab-api-token"),
  format="ocsf"
```

With `format="ocsf"`, the operator returns the OCSF 1.6.0 events of the Splunk
export. With `format="ecs"`, it returns the ECS documents of the Elastic
export. The events arrive unchanged. The Manager removes every event it
returns, so run only one pipeline per format.

An example shows how to read the S3 export instead, which leaves the events in
the bucket.
