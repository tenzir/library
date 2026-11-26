The HarfangLab package now reduces the event volume before a SIEM, for OCSF and ECS, and keeps HarfangLab IOC sources in sync with threat intelligence feeds.

## 🚀 Features

### HarfangLab reduction operators

The `harfanglab` package now includes operators that reduce the volume of HarfangLab events for a SIEM, for both OCSF events and ECS documents:

```tql
every 1min {
  harfanglab::fetch "https://example.hurukai.io:8443",
    token=secret("harfanglab-api-token")
}
harfanglab::ocsf::reduce
```

- `summarize_network` and `summarize_http` summarize network connections and HTTP requests per five minutes.
- `deduplicate_processes` and `deduplicate_modules` forward the first start of each process and the first load of each module by each executable per hour unchanged and summarize the repeats.
- `reduce` applies all four and passes every other event through unchanged.

Each operator exists as `harfanglab::ocsf::…` and `harfanglab::ecs::…`. The results stay events of the same OCSF class or ECS category. Summaries carry `count` (OCSF) or `tenzir.count` (ECS), so a SIEM must sum these to count events.

The operators keep about 2 to 5 KB per summary in memory until its window closes. The package description explains how to size a node.

*By @zedoraps in #276.*

### IOC sync to HarfangLab

The new `harfanglab::ioc::sync` operator keeps an IOC source of a HarfangLab Manager in sync with a feed of indicators:

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

- One call handles one indicator type: `domain`, `ip`, `sha256`, `sha1`, `md5`, `filename`, `filepath`, or `url`.
- It reads the source once per run and only sends requests for differences, so an unchanged feed causes no writes.
- Expired and revoked indicators are disabled or deleted, and `prune=true` disables indicators that left the feed.
- A run stops before any write when pruning would disable more than `max_prune` IOCs (10) and more than `max_prune_share` of the source (10%), or when the Manager returns an incomplete listing.
- `dry_run=true` shows what a run would do without writing.
- IOCs alert by default. Blocking states need `allow_blocking=true`.
- Every indicator yields a result event with the action taken, and invalid values yield `failed` results without a request.

*By @zedoraps.*
