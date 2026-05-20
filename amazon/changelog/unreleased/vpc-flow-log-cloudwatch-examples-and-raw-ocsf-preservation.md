---
title: CloudWatch examples and raw OCSF preservation
type: feature
authors:
  - mavam
  - codex
created: 2026-05-20T13:20:50.623334Z
---

The Amazon package now includes source-agnostic VPC Flow Log parsing helpers and examples for CloudWatch and S3 workflows.

Use the `into` argument when you need to keep source metadata or the raw log line alongside the parsed record:

```tql
from_amazon_cloudwatch "/aws/vpc/flowlogs", mode="search"
amazon::vpc_flow::parse_v7_ecs field=message, into=vpc_flow
amazon::vpc_flow::to_ocsf vpc_flow, raw=message
ocsf::cast
```

The VPC Flow Log and Route 53 OCSF mappings preserve `raw_data` and `raw_data_size` when a raw field is provided.
