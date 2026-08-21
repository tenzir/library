---
title: Event-scoped OCSF mapping operators
type: breaking
authors:
  - mavam
  - codex
created: 2026-06-13T07:58:15.702248Z
---

`checkpoint::ocsf::map` now takes an optional positional source field and a
named `into` output. Both default to `this`, and exact in-place mapping is safe:

```tql
checkpoint::ocsf::map source, into=ocsf
```

The mapper targets OCSF 1.9. URL and Application Control records now use HTTP
Activity because OCSF deprecated Web Resource Access Activity.
