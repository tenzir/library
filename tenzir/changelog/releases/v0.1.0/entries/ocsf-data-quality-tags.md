---
title: OCSF data quality tags
type: feature
authors:
  - mavam
prs:
  - 236
created: 2026-11-16T12:00:00Z
---

The new `tenzir::ocsf::quality` operator tags data quality problems of OCSF
events of any class. It appends one `{name, value}` entry per problem to
`metadata.tags`, naming the quality dimension and the affected attribute:

| Name | Value | Fires when |
|---|---|---|
| `quality.completeness` | `truncated` | `metadata.is_truncated` is true |
| `quality.completeness` | a `required` path | the attribute is missing or null |
| `quality.validity` | `activity_id` | missing, Unknown (0), or Other (99) |
| `quality.validity` | `status_id` | present and Unknown (0) or Other (99) |
| `quality.consistency` | `type_uid` | not `class_uid * 100 + activity_id` |
| `quality.timeliness` | `time` | more than `tolerance` (5min) in the future |

Pass class-specific completeness requirements as comma-separated paths:

```tql
accept_udp "0.0.0.0:514"
this = data.parse_syslog()
paloalto::ocsf::normalize
tenzir::ocsf::quality required="src_endpoint.ip, dst_endpoint.ip, dst_endpoint.port"
to_splunk "https://splunk.example.com:8088", hec_token=secret("splunk-hec-token")
```

The operator keeps existing tags, leaves clean events untouched, and never
drops events.
