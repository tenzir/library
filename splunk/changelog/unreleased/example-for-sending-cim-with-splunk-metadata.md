---
title: Example for sending CIM with Splunk metadata
type: feature
authors:
  - zedoraps
created: 2026-11-20T19:42:03.402861Z
---

A new example sends CIM to Splunk HEC with metadata from the OCSF event, because the CIM record carries no `host`, `source`, `sourcetype`, or `time`:

```tql
this = {ocsf: this}
splunk::cim::from_ocsf ocsf, into=cim
to_splunk "https://localhost:8088", hec_token=secret("SPLUNK_HEC_TOKEN"),
  event=cim, host=ocsf.device?.hostname?, time=ocsf.time
```
