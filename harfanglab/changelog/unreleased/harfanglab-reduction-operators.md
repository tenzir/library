---
title: HarfangLab reduction operators
type: feature
authors:
  - zedoraps
created: 2026-11-26T17:14:02.193052Z
---

The `harfanglab` package now includes operators that reduce the volume of
HarfangLab events for a SIEM, for both OCSF events and ECS documents:

```tql
every 1min {
  harfanglab::fetch "https://example.hurukai.io:8443",
    token=secret("harfanglab-api-token")
}
harfanglab::ocsf::reduce
```

- `summarize_network` and `summarize_http` summarize network connections and
  HTTP requests per five minutes.
- `deduplicate_processes` and `deduplicate_modules` deduplicate process
  starts per hour and module loads per day.
- `reduce` applies all four and passes every other event through unchanged.

Each operator exists as `harfanglab::ocsf::…` and `harfanglab::ecs::…`. The
results stay events of the same OCSF class or ECS category. OCSF results
carry `count`, `start_time`, and `end_time`, ECS results `event.start`,
`event.end`, and `tenzir.count`.
