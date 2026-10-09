---
title: OSINT enrichment honors IP matches and expiration
type: bugfix
authors:
  - mavam
prs:
  - 196
created: 2026-10-09T15:05:46.783122Z
---

The OSINT lookup table now honors indicator expiration, and IP enrichment works with every OSINT feed.

- `tenzir::osint::enrich` matches IP addresses against the string values that OSINT mappers store, so network events now get IP indicator matches. It also ignores indicators past their `expiration_time` and adds `osint` and the `osint` profile only to events with a match.
- `tenzir::osint::update_context` erases indicators whose `expiration_time` has passed and no longer warns about events without a status.
