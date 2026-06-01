---
title: MISP OCSF mapping and sightings for v6
type: breaking
authors:
  - mavam
  - codex
prs:
  - 147
created: 2026-05-31T19:12:55Z
---

MISP event normalization and sighting submission now work with the v6 executor.

Use the reusable OCSF mapper for fetched MISP events, and submit sightings with
`each` and `from_http` in your own pipeline:

```tql
misp::event::ocsf::map
```

Existing pipelines that relied on packaged sighting submission should move that
HTTP call into an explicit workflow.
