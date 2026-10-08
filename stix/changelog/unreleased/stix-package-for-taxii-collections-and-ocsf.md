---
title: STIX package for TAXII collections and OCSF
type: feature
authors:
  - mavam
created: 2026-10-08T18:09:09.708691Z
---

The new `stix` package fetches STIX 2.1 objects from TAXII 2.1 collections and maps STIX Indicators to OCSF 1.9 OSINT Inventory Info. Revoked indicators carry the `Removed` status, so `tenzir::osint::update_context` erases them from the OSINT lookup table:

```tql
stix::taxii::fetch "https://taxii.example.com/api-root/collections/indicators/objects/",
  headers={Authorization: f"Basic {secret("TAXII_CREDENTIAL")}"}
where type == "indicator"
stix::ocsf::normalize
tenzir::osint::update_context
```
