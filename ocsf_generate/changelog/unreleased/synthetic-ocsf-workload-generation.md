---
title: Synthetic OCSF workload generation
type: feature
authors:
  - zedoraps
created: 2026-10-27T15:23:50.354438Z
---

Generate finite datasets, paced live streams, and historical traffic with the new `ocsf_generate` package. It covers all concrete OCSF 1.9 core and Windows event classes plus Base Event, with reusable organization fixtures, optional profile context, and product-specific raw logs.

```tql
ocsf_generate::generate count=100000
```

Use `ocsf_generate::generate_load eps=1000` for a continuous stream. Exact-count IOC needles, configurable observables, and optional schema drift support lookup and robustness tests.
