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

The alphaMountain package now exposes reusable operators for API lookups, feeds, and OCSF OSINT mapping.

Use the namespaced operators directly in your own workflows:

```tql
alphamountain::threat::feed license="ALPHAMOUNTAIN_LICENSE", limit=100
alphamountain::ocsf::map
ocsf::derive
ocsf::cast
```

The package covers real-time URI lookups, hostname intelligence, threat and category feeds, ranked feeds, license information, support APIs, category metadata, and CSV parsing. It also ships anonymized fixture coverage for API response shapes, CSV parsing behavior, and OCSF mapping paths.

CSV response parsing is centralized in `alphamountain::read`, while OCSF-specific category label derivation lives in `alphamountain::ocsf::map`. Use `tenzir::osint::update_context` from the Tenzir utilities package to load mapped OSINT events into a shared OCSF OSINT context.
