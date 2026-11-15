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

Normalize a structured Windows Event Log or Microsoft Graph record before
translating it to ASIM:

```tql
microsoft::windows::ocsf::normalize
microsoft::asim::from_ocsf
```

Use `microsoft::graph::ocsf::normalize` instead for Microsoft Graph records.

The ASIM translator covers authentication, process, audit, user-management,
alert, file, network, DNS, DHCP, and web session schemas.
