---
title: Event-scoped CIM and OCSF mapping operators
type: breaking
authors:
  - mavam
  - codex
created: 2026-06-13T07:58:24.616664Z
---

Splunk CIM and OCSF mapping operators now take a named `event` field argument that defaults to `this` and perform all mapping work inside that explicit event scope.

The canonical OCSF-to-CIM mapper remains `splunk::cim::ocsf::map`, and the CIM-to-OCSF mapper remains `splunk::ocsf::cim::map`.

Before:

```tql
splunk::cim::ocsf::map
```

After:

```tql
splunk::cim::ocsf::map event=ocsf_event
```
