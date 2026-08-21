---
title: OCSF to ASIM mapper
type: feature
authors:
  - mavam
  - codex
prs:
  - 153
created: 2026-06-07T00:00:00Z
---

The Microsoft package includes `microsoft::asim::from_ocsf` for translating
validated OCSF 1.9 events into flat Microsoft Sentinel ASIM records. It takes an
optional positional source field and a named `into` output, both defaulting to
`this`.

Windows Event Log and Microsoft Graph source mappings use their source
namespaces:

```tql
microsoft::windows::ocsf::map windows, into=ocsf
microsoft::graph::ocsf::map graph, into=ocsf
microsoft::asim::from_ocsf ocsf, into=asim
```

The ASIM translator covers authentication, process, audit, user-management,
alert, file, network, DNS, DHCP, and web session schemas.
