---
title: Single Geo Open context
type: change
authors:
  - mavam
  - claude
created: 2025-12-16T07:11:11.89317Z
---

The package now ships one default `geo-open` GeoIP context instead of separate
country and country+ASN contexts. Use `context::load` to populate it with either
Geo Open MMDB variant, and `context::enrich` to query it from pipelines.
