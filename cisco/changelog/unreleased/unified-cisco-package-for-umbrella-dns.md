---
title: Unified Cisco package for Umbrella DNS
type: breaking
authors:
  - mavam
  - codex
prs:
  - 147
created: 2026-05-31T19:12:55Z
---

Cisco Umbrella DNS support now lives in the unified `cisco` package.

Use the new namespaced operators for file, S3, and OCSF workflows:

```tql
cisco::umbrella::dns::read
cisco::umbrella::ocsf::map
```

Installations that previously depended on the legacy Cisco Umbrella package
must switch to the `cisco::umbrella::*` operator names.
