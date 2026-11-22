---
title: Example for sending CIM with Splunk metadata
type: feature
authors:
  - zedoraps
prs:
  - 261
created: 2026-11-22T12:00:10.788561Z
---

A new example sends CIM to Splunk HEC and takes `host` and `time` from the OCSF event, since the CIM record carries no Splunk metadata:

```tql
this = {ocsf: this}
splunk::cim::from_ocsf ocsf, into=cim
to_splunk "https://localhost:8088", hec_token=secret("SPLUNK_HEC_TOKEN"),
  event=cim, host=ocsf.device?.hostname?, time=ocsf.time
```
