---
title: Consolidate Amazon packages into unified `amazon` package
type: breaking
authors:
  - mavam
  - claude
components:
  - amazon
created: 2025-12-18T00:00:00Z
---

Merged `amazon_security_lake` and `amazon_vpc_flow` packages into a single
unified `amazon` package with namespaced operators:

- `amazon::vpc_flow::parse` - Parse CloudWatch events with custom header using `parse_ssv`
- `amazon::vpc_flow::parse_v2` - Parse default AWS format (14 fields)
- `amazon::vpc_flow::parse_v7_ecs` - Parse v7 format with ECS fields (24 fields)
- `amazon::vpc_flow::to_ocsf` - Map to OCSF Network Activity (class 4001)
- `amazon::security_lake::cast` - Cast OCSF events for Security Lake compatibility
- `amazon::security_lake::send` - Send OCSF events to Security Lake

The VPC Flow Log parsers now expect CloudWatch events with a `message` field
containing the flow log line, and automatically convert `start`/`end` fields
from Unix epoch seconds to proper timestamps.

This replaces the separate `amazon_security_lake` and `amazon_vpc_flow` packages.
