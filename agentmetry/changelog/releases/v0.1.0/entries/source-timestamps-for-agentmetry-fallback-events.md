---
title: Source timestamps for Agentmetry fallback events
type: bugfix
authors:
  - mavam
prs:
  - 225
created: 2026-11-10T08:17:51.472009Z
---

Agentmetry normalization now maps `timestamp_utc` to the OCSF event time even when the record has no action type and becomes a Base Event. Records without a timestamp still have no event time; the mapping does not invent one.
