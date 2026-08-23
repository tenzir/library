---
title: Directional CIM and OCSF translation operators
type: breaking
authors:
  - mavam
  - codex
created: 2026-06-13T07:58:24.616664Z
---

Public Splunk schema translation uses directional operators. The source field
is positional and defaults to `this`; the named `into` output also defaults to
`this`.

```tql
splunk::ocsf::from_cim cim, into=ocsf
splunk::cim::from_ocsf ocsf, into=cim
```

Detailed mapping helpers remain internal under the schema-pair namespaces.
