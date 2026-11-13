## 🚀 Features

### Add isMalicious indicator reputation lookups

The new `ismalicious` package looks up the reputation of IP addresses, domains, URLs, and file hashes. Use `ismalicious::check` to fetch risk scores, evidence, and provenance from the isMalicious API:

```tql
ismalicious::check query="192.0.2.1",
  api_credential=secret("ISMALICIOUS_API_CREDENTIAL")
```

### isMalicious feeds for the OSINT lookup table

The `ismalicious` package now loads the isMalicious STIX/TAXII feeds. `ismalicious::feed` fetches the indicators of a collection, such as `malicious-domains` or `malicious-ips`, and `ismalicious::ocsf::normalize` maps them to OCSF OSINT Inventory Info for the OSINT lookup table:

```tql
ismalicious::feed "malicious-ips",
  api_credential=secret("ISMALICIOUS_API_CREDENTIAL"),
  params={min_score: 60}
ismalicious::ocsf::normalize
tenzir::osint::update_context
```

Pass `added_after` to poll for new indicators and revocations between daily walks. Revoked indicators stop matching.

*By @mavam in #196.*

## 🐞 Bug fixes

### Dependency on the stix package

The `ismalicious` package now declares that it uses the `stix` package for fetching and normalizing its TAXII feeds, so installing `ismalicious` brings `stix` along. Tenzir 7 lets a package use only the packages it declares.

The OSINT lookup table now lives in your configuration:

```yaml
# contexts/ocsf-osint.yaml
type: lookup-table
persist-interval: 5min
write-timeout: 30d
```

*By @mavam in #233.*
