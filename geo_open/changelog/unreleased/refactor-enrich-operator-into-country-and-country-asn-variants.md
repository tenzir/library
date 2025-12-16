---
title: Add OCSF enrichment operators and simplify package
type: change
authors:
  - mavam
  - claude
created: 2025-12-16T07:11:11.89317Z
---

Adds two specialized operators for enriching OCSF Network Activity events:

- `geo_open::enrich::ocsf::country` for country-only enrichment
- `geo_open::enrich::ocsf::country_asn` for country and ASN enrichment

Removes the subscribe/publish pipeline in favor of using UDOs directly in user pipelines.
