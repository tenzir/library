---
title: Windows event demo source
type: feature
authors:
  - zedoraps
created: 2026-08-27T00:00:00Z
---

The new `demo::windows` operator replays raw Windows events captured in a test lab as Winlogbeat NDJSON, Fluent Bit NDJSON, or Windows Event Log XML. Pair it with the `microsoft` package to demonstrate collector-independent normalization to OCSF:

```tql
demo::windows "winlogbeat"
event = line.parse_json()
microsoft::windows::ocsf::normalize event, into=ocsf
this = move ocsf
```
