---
title: IOC sync to HarfangLab
type: feature
authors:
  - zedoraps
created: 2026-11-26T19:06:54.690333Z
---

The new `harfanglab::ioc::sync` operator keeps an IOC source of a HarfangLab
Manager in sync with a feed of indicators:

```tql
every 1h {
  from_http "https://feeds.example.org/malicious-domains.txt" {
    read_lines
  }
  line = line.trim()
  where line != "" and not line.starts_with("#")
  harfanglab::ioc::sync "https://example.hurukai.io:8443",
    token=secret("harfanglab-api-token"),
    source="tenzir-threat-domains",
    type="domain",
    value=line,
    prune=true,
    max_prune_share=0.1
}
```

- One call handles one indicator type: `domain`, `ip`, `sha256`, `sha1`,
  `md5`, `filename`, `filepath`, or `url`.
- It reads the source once per run and only sends requests for differences,
  so an unchanged feed causes no writes.
- Expired and revoked indicators are disabled or deleted, and `prune=true`
  disables indicators that left the feed.
- A run stops before any write when pruning would disable more than
  `max_prune` IOCs (10) and more than `max_prune_share` of the source (10%),
  or when the Manager returns an incomplete listing.
- `dry_run=true` shows what a run would do without writing.
- IOCs alert by default. Blocking states need `allow_blocking=true`.
- Every indicator yields a result event with the action taken, and invalid
  values yield `failed` results without a request.
