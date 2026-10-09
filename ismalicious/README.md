# isMalicious

[isMalicious](https://ismalicious.com) provides reputation data for IP
addresses, domains, URLs, and MD5, SHA-1, or SHA-256 hashes. Load its feeds
into a lookup table to enrich events in the stream, and look up individual
indicators during investigations.

## Configure credentials

Create an [API key and secret](https://ismalicious.com/app/account), then store
the Base64 encoding of `apiKey:apiSecret` in the managed secret
`ISMALICIOUS_API_CREDENTIAL`. The API expects this value in the `X-API-KEY`
header.

## Load the feeds

`ismalicious::feed` fetches the STIX 2.1 Indicators of a TAXII collection, such
as `malicious-domains` or `malicious-ips`. TAXII access requires a Pro or
Enterprise plan. `ismalicious::ocsf::normalize` maps the indicators to OCSF
OSINT Inventory Info, which the `tenzir` package loads into its OSINT lookup
table:

```tql
ismalicious::feed "malicious-ips",
  api_credential=secret("ISMALICIOUS_API_CREDENTIAL"),
  params={min_score: 60}
ismalicious::ocsf::normalize
tenzir::osint::update_context
```

The collections hold millions of indicators. The operator pages at the plan's
rate limit. `min_score` keeps indicators with an OpenCTI risk score of at least
the given value, but the server still scans the whole collection, so a walk of
both collections takes over an hour.

## Keep the table current

Combine two schedules, as the examples show:

- `examples/update-osint-context.tql` walks both collections daily, after the
  provider's nightly reload, and updates every indicator in the table.
- `examples/poll-osint-updates.tql` polls between walks with `added_after`,
  which adds new indicators and delivers revocations. Each poll looks back a
  day, so a few failed polls lose nothing.

Only walks with `added_after` deliver revocations, and isMalicious keeps them
for 30 days. A revoked indicator leaves the table, and an indicator past its
`valid_until` stops matching and leaves on the next update. Indicators that the
feed no longer serves age out after `max_age`. The table updates page by page,
so an interrupted walk leaves the pages it already applied.

The operator requires the `stix` package.

## Look up an indicator

`ismalicious::check` performs one lookup with standard enrichment and returns
the API response as a single event:

```tql
ismalicious::check query="192.0.2.1",
  api_credential=secret("ISMALICIOUS_API_CREDENTIAL")
```

To enrich existing events, call the operator inside `each`:

```tql
each {
  ismalicious::check query=$this.indicator,
    api_credential=secret("ISMALICIOUS_API_CREDENTIAL")
  this = {...$this, ismalicious: this}
}
```

Each lookup counts against your account quota, so deduplicate indicators
before enriching high-volume streams.

## Interpret results

Read `evidence.verdict` together with `evidence.reasons` and
`evidence.contradictorySignals`. `malicious: false` does not prove that an
indicator is safe; unknown hashes and context-only sources yield an `unknown`
verdict. `confidence` is independent of `riskScore`.

See the [API reference](https://ismalicious.com/api-docs) for all fields.
