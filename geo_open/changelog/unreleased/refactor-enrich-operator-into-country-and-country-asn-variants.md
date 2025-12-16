---
title: OCSF enrichment operator with optional ASN support
type: change
authors:
  - mavam
  - claude
created: 2025-12-16T07:11:11.89317Z
---

The new `geo_open::enrich` operator enriches OCSF Network Activity events
with country information. Use `asn=true` to include Autonomous System Number
data.

The previous subscribe/publish pipeline pattern has been replaced with direct
UDO usage in user pipelines.
