---
title: Simplify Zscaler OCSF mapping
type: change
authors:
  - mavam
  - codex
prs:
  - 147
created: 2026-05-31T19:12:55Z
---

The `zscaler::ocsf::map` operator now owns the shared OCSF setup, event
dispatch, and finalization for ZIA NSS web logs. Event-specific OCSF operators
focus on class-specific fields, and HTTP methods now use OCSF 1.8 activity IDs.
