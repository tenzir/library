---
title: Zeek OCSF 1.8 metadata
type: change
authors:
  - mavam
  - codex
prs:
  - 147
created: 2026-05-31T19:12:55Z
---

Zeek mappings now target OCSF 1.8.0, the latest stable OCSF schema version used
by the library.

Events produced by `zeek::ocsf::map` now advertise
`metadata.version: "1.8.0"`. Review downstream validation, dashboards, and
schema checks that matched on the previous OCSF metadata version.
