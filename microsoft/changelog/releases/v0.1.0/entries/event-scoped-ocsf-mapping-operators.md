---
title: Unified Windows Event Log normalization
type: breaking
authors:
  - mavam
  - codex
prs:
  - 180
created: 2026-06-13T07:58:23.948112Z
---

The standalone `sysmon` package is now part of the `microsoft` package. Use one
provider-aware entry point for Sysmon and other Microsoft Windows Event Log
events:

```tql
microsoft::windows::ocsf::normalize
```

For staged processing, use `microsoft::windows::canonicalize` followed by
`microsoft::windows::ocsf::map`. The mapper dispatches by provider before event
ID so event ID collisions cannot select a mapping for another provider.
