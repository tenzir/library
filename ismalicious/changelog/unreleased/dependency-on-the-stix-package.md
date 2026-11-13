---
title: Dependency on the stix package
type: bugfix
authors:
  - mavam
created: 2026-11-13T11:32:39.221757Z
---

The `ismalicious` package now declares that it uses the `stix` package for
fetching and normalizing its TAXII feeds, so installing `ismalicious` brings
`stix` along. Tenzir 7 lets a package use only the packages it declares.

The OSINT lookup table now lives in your configuration:

```yaml
# contexts/ocsf-osint.yaml
type: lookup-table
persist-interval: 5min
write-timeout: 30d
```
