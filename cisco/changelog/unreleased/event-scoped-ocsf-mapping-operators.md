---
title: Event-scoped OCSF mapping operators
type: breaking
authors:
  - mavam
  - codex
created: 2026-06-13T07:58:16.435958Z
---

OCSF mapping operators now take a named `event` field argument that defaults to `this` and perform all mapping work inside that explicit event scope.

Before:

```tql
pkg::ocsf::map source
```

After:

```tql
pkg::ocsf::map event=source
```
