---
title: OCSF to CIM DNS mapping
type: feature
authors:
  - mavam
  - codex
created: 2026-06-07T16:30:12Z
---

The Splunk package can now map OCSF DNS Activity events to Splunk CIM Network
Resolution DNS fields:

```tql
splunk::cim::map
```

Use this compatibility layer before detection logic that expects fields such as
`query`, `answer`, `reply_code`, `reply_code_id`, `query_type`,
`transaction_id`, `response_time`, `src`, and `vendor_product`.
