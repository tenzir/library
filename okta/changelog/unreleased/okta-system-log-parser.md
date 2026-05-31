---
title: Okta System Log parser
type: breaking
authors:
  - mavam
  - codex
prs:
  - 147
created: 2026-05-31T19:12:55Z
---

Okta System Log parsing now starts with `okta::read`.

Use `okta::read` after any byte source, then map the normalized events to OCSF:

```tql
from_http "https://example.okta.com/api/v1/logs"
okta::read
okta::ocsf::map
```

Pipelines that used the removed `okta::clean` operator should switch to this
parser-based flow.
