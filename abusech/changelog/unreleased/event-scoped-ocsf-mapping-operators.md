---
title: OCSF 1.9 mapping contracts
type: breaking
authors:
  - mavam
  - codex
created: 2026-06-13T07:58:14.148769Z
---

abuse.ch OCSF mappers now take an optional positional source field and a named
`into` output. Both default to `this`.

```tql
abusech::threatfox::ocsf::map indicator, into=ocsf
```

The MalwareBazaar and ThreatFox API response helpers are now named `unwrap`.
They split API response envelopes into source rows and are not OCSF
normalizers.
