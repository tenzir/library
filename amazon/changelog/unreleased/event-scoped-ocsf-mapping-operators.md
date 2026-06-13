---
title: Event-scoped OCSF mapping operators
type: breaking
authors:
  - mavam
  - codex
created: 2026-06-13T07:58:00.996294Z
---

OCSF mapping operators now take a named `event` field argument that defaults to `this` and perform all mapping work inside that explicit event scope.

Before:

```tql
amazon::vpc_flow::ocsf::map vpc_flow, raw=message
```

After:

```tql
amazon::vpc_flow::ocsf::map event=vpc_flow
vpc_flow.raw_data = move message
vpc_flow.raw_data_size = vpc_flow.raw_data.length_bytes()
this = vpc_flow
```
