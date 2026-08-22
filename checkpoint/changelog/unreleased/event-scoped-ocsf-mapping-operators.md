---
title: Event-scoped OCSF mapping operators
type: breaking
authors:
  - mavam
  - codex
created: 2026-06-13T07:58:15.702248Z
---

`checkpoint::ocsf::map` takes the structured source and OCSF output fields
positionally:

```tql
checkpoint::ocsf::map source, ocsf
```

The mapper targets OCSF 1.9. URL and Application Control records now use HTTP
Activity because OCSF deprecated Web Resource Access Activity.
