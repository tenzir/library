---
title: OCSF 1.9 normalization contracts
type: breaking
authors:
  - mavam
  - codex
created: 2026-06-13T07:58:14.148769Z
---

Use the feed-specific `normalize` operators to turn structured abuse.ch rows
into OCSF 1.9 events:

```tql
abusech::threatfox::ocsf::normalize
```
