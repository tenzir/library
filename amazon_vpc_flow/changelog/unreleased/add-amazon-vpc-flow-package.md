---
title: Add `amazon_vpc_flow` package
type: feature
authors:
- mavam
- claude
components:
- amazon_vpc_flow
created: 2025-12-12T14:59:22.380486Z
---

The new package provides parsing and OCSF mapping for Amazon VPC Flow Logs.

Use `amazon_vpc_flow::parse` with a custom header for any field configuration,
or `amazon_vpc_flow::parse_v2` for the default AWS format. The `to_ocsf`
operator maps parsed logs to OCSF Network Activity events (class 4001).
