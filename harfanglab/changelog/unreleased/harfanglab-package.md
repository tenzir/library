---
title: HarfangLab package
type: feature
authors:
  - zedoraps
prs:
  - 275
created: 2026-11-26T15:39:51.849895Z
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

Examples show how to read the S3 export instead, which leaves the events in the
bucket, and how to reduce the volume for a SIEM: summarize network activity,
deduplicate process starts and module loads, and forward findings and audit
events in full.
