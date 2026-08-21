---
title: CloudWatch examples and raw OCSF preservation
type: feature
authors:
  - mavam
  - codex
prs:
  - 147
created: 2026-05-20T13:20:50.623334Z
---

The Amazon package includes source-agnostic VPC Flow Log parsing helpers and
examples for CloudWatch and S3 workflows. The normalizer preserves the source
line as OCSF provenance:

```tql
from_amazon_cloudwatch "/aws/vpc/flowlogs", mode="search"
amazon::vpc_flow::ocsf::normalize message
ocsf::cast
```

Use the parser and mapper separately when the pipeline needs the structured VPC
Flow Log record before mapping.
