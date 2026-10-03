# IsMalicious

`ismalicious::check` makes one API reputation lookup for an IPv4/IPv6 address,
domain, URL, MD5, SHA-1 or SHA-256. It preserves the JSON response, including
risk score, confidence, evidence verdict/reasons, contradictory signals,
provenance, `lookupStatus`, `knownGood` and delisting flags where present.

Create an [account and API key/secret pair](https://ismalicious.com/app/account).
Set the managed secret `ISMALICIOUS_API_CREDENTIAL` to **Base64 of
`apiKey:apiSecret`**, which is the value expected in `X-API-KEY`. The API key
component alone is insufficient. Do not commit credentials into pipelines.

```tql
ismalicious::check query="192.0.2.1",
  api_credential=secret("ISMALICIOUS_API_CREDENTIAL")
```

This example uses a documentation IP; replace it with an indicator from your
investigation. See `examples/enrich-events.tql` to retain the original event.
Standard enrichment is requested. Available fields vary by indicator and
account; the operator does not claim timeline data from full enrichment.

Interpret `evidence.verdict` and its reasons/contradictions. `malicious: false`
does not prove safety, and a zero risk score on an unknown hash stays unknown.
Confidence is distinct from risk score. Context-only source rows are not a
count of detections. The package does not apply tags or block devices.

Empty or whitespace-only indicators are dropped with a diagnostic before any
request. Requests use TLS verification and a 30-second timeout by default. The operator
makes no automatic retries: authentication, quota/rate-limit, server and
transport errors are diagnosed by `from_http`, rather than emitted as clean
reports. Redirect responses are not followed; unexpected 3xx responses are
dropped with a diagnostic. Check the diagnostic and retry later as appropriate. An administrator
can configure `base_url` for a trusted proxy; it must not come from an IOC.
Each call consumes a lookup under your account quota. This package does not
consume or redistribute paid TAXII feeds.

API reference: <https://ismalicious.com/api-docs>.

Tested with Tenzir v6.19.1. Tests use a local HTTP fixture and explicitly
synthetic response data. Run
`uvx --with tenzir tenzir-test ismalicious` from the library root.
