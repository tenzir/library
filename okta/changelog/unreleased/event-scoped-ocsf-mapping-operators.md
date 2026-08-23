---
title: OCSF 1.9 normalization contract
type: breaking
authors:
  - mavam
  - codex
created: 2026-06-13T07:58:19.553916Z
---

Use `okta::ocsf::normalize` to normalize structured Okta System Log events to OCSF 1.9:

```tql
okta::ocsf::normalize
```

The lower-level `okta::ocsf::map` operator remains available for pipelines that need
separate structured source and OCSF output fields.
