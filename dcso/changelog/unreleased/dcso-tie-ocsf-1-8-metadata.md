---
title: DCSO TIE OCSF 1.9 metadata
type: change
authors:
  - mavam
  - codex
prs:
  - 147
created: 2026-05-31T19:12:55Z
---

DCSO TIE mappings now target OCSF 1.9.0, the latest stable OCSF schema version
used by the library.

Events produced by `dcso::tie::ocsf::normalize` now advertise
`metadata.version: "1.9.0"`. Review downstream validation or routing rules that
match on the previous OCSF metadata version.
