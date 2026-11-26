---
title: HarfangLab reduction operators
type: feature
authors:
  - zedoraps
created: 2026-11-26T17:14:02.193052Z
---

The `harfanglab` package now includes operators that reduce the volume of
HarfangLab OCSF events for a SIEM:

```tql
every 1min {
  harfanglab::fetch "https://example.hurukai.io:8443",
    token=secret("harfanglab-api-token")
}
harfanglab::ocsf::reduce
```

- `harfanglab::ocsf::summarize_network` and
  `harfanglab::ocsf::summarize_http` summarize Network and HTTP Activity per
  five minutes.
- `harfanglab::ocsf::deduplicate_processes` and
  `harfanglab::ocsf::deduplicate_modules` deduplicate process starts per hour
  and module loads per day.
- `harfanglab::ocsf::reduce` applies all four and passes every other event
  through unchanged.

The results stay events of the same OCSF class, with `count`, `start_time`,
and `end_time` describing the events they stand for.
