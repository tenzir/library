---
title: isMalicious feeds for the OSINT lookup table
type: feature
authors:
  - mavam
prs:
  - 196
created: 2026-10-09T12:57:51.475826Z
---

The `ismalicious` package now loads the isMalicious STIX/TAXII feeds. `ismalicious::feed` fetches the indicators of a collection, such as `malicious-domains` or `malicious-ips`, and `ismalicious::ocsf::normalize` maps them to OCSF OSINT Inventory Info for the OSINT lookup table:

```tql
ismalicious::feed "malicious-ips",
  api_credential=secret("ISMALICIOUS_API_CREDENTIAL"),
  params={min_score: 60}
ismalicious::ocsf::normalize
tenzir::osint::update_context
```
