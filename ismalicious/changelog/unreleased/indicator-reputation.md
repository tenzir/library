---
title: Add IsMalicious indicator reputation lookups
type: feature
---

The new `ismalicious` package looks up the reputation of IP addresses, domains,
URLs, and file hashes. Use `ismalicious::check` to fetch risk scores, evidence,
and provenance from the IsMalicious API:

```tql
ismalicious::check query="192.0.2.1",
  api_credential=secret("ISMALICIOUS_API_CREDENTIAL")
```
