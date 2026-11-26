The new HarfangLab package fetches OCSF events and ECS documents from a HarfangLab Manager through its pull exports, with an example for the S3 export.

## 🚀 Features

### HarfangLab package

The library now includes a `harfanglab` package that fetches events from a [HarfangLab](https://harfanglab.io/) Manager through its pull exports:

```tql
harfanglab::fetch "https://example.hurukai.io:8443",
  token=secret("harfanglab-api-token"),
  format="ocsf"
```

With `format="ocsf"`, the operator returns the OCSF 1.6.0 events of the Splunk export. With `format="ecs"`, it returns the ECS documents of the Elastic export. The events arrive unchanged. The Manager removes every event it returns, so run only one pipeline per format.

An example shows how to read the S3 export instead, which leaves the events in the bucket.

*By @zedoraps in #275.*
