---
title: Consolidated abuse.ch feeds
type: breaking
authors:
  - mavam
  - codex
prs:
  - 147
created: 2026-05-31T19:12:55Z
---

The abuse.ch feeds now install as one `abusech` package instead of separate
feed-specific packages.

Use the namespaced feed operators to fetch and map threat intelligence from
Feodo Tracker, MalwareBazaar, SSLBL, ThreatFox, and URLhaus:

```tql
abusech::threatfox::fetch
abusech::threatfox::ocsf::map
```

Installations that previously used the standalone abuse.ch feed packages must
switch to the corresponding `abusech::*` operators.
