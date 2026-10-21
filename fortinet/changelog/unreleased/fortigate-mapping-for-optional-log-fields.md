---
title: FortiGate mapping for optional log fields
type: bugfix
authors:
  - zedoraps
created: 2026-10-21T12:29:05.324049Z
---

FortiGate logs that provide `eventtime` without separate date and time fields now map without missing-field warnings. Explicit proxy traffic can omit packet counts, and authentication throttling alerts can omit usernames and endpoint IPs. Missing values remain absent rather than becoming invented counters or identities.
