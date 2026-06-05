---
title: alphaMountain API operators and OCSF mapping
type: feature
authors:
  - mavam
  - codex
prs:
  - 150
created: 2026-06-05T07:36:42.46596Z
---

The alphaMountain package now exposes reusable operators for API lookups, feeds, batch diffs, and OCSF OSINT mapping.

Use the namespaced operators directly in your own workflows:

```tql
alphamountain::threat::feed license="ALPHAMOUNTAIN_LICENSE", limit=100
alphamountain::ocsf::map
ocsf::derive
ocsf::cast
```

The package covers real-time URI lookups, hostname intelligence, threat and category feeds, and batch diffs. It also ships anonymized OCSF mapping coverage that derives and casts the resulting events.

OCSF-specific category label derivation lives in `alphamountain::ocsf::map`. Use `tenzir::osint::update_context` from the Tenzir utilities package to load mapped OSINT events into a shared OCSF OSINT context.
