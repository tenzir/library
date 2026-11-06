---
title: Synthetic OCSF workload generation
type: feature
authors:
  - zedoraps
prs:
  - 207
created: 2026-10-27 15:23:50.354438+00:00
---

Generate finite datasets, paced live streams, and historical traffic with the new `ocsf_generate` package. It covers all concrete OCSF 1.9 core and Windows event classes plus Base Event, with reusable organization fixtures, optional profile context, and product-specific raw logs.

```tql
ocsf_generate::generate count=100000
```

Use `ocsf_generate::generate_load eps=1000` for a continuous stream. Exact-count IOC needles, configurable observables, and optional schema drift support lookup and robustness tests.

Generate OCSF 1.6.0 file, process, authentication, network, and DNS events with the dedicated legacy operator:

```tql
ocsf_generate::generate_legacy count=10000
```

Merge its output with `ocsf_generate::generate` to test mixed schema versions. The legacy events use their version's field layout and share the organization fixtures with the 1.9 workload.
