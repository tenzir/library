---
title: Windows event demo source
type: feature
authors:
  - zedoraps
created: 2026-08-27T00:00:00Z
---

The new `demo::windows` operator replays a raw Windows test-lab capture in
real time, in your choice of three collector representations: Winlogbeat
NDJSON, Fluent Bit NDJSON, or Windows Event Log XML. Each replay moves the
capture to the current timeline, rewrites the timestamps embedded in the raw
payloads, and rotates events across three demo hostnames. Every representation
contains the same 34 provider/event-code combinations, which normalize into 24
distinct OCSF activities. The default replay rate averages 1.5 events per
second. Adjust `speed` to increase or decrease the rate. Pair the source with
the `microsoft` package to demonstrate
collector-independent normalization to OCSF:

```tql
demo::windows "winlogbeat"
event = raw.parse_json()
microsoft::windows::ocsf::normalize event, into=ocsf
this = move ocsf
```
