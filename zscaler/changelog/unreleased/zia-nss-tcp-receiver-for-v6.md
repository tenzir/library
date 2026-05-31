---
title: ZIA NSS TCP receiver for v6
type: breaking
authors:
  - mavam
  - codex
prs:
  - 147
created: 2026-05-31T19:12:55Z
---

ZIA NSS TCP receiver examples now use the v6 network source syntax.

Replace TCP receivers that used the old source form with `accept_tcp`:

```tql
from "tcp://0.0.0.0:9014" {
  read_lines
}
zscaler::ocsf::map
```

This keeps Zscaler onboarding pipelines compatible with the v6 executor.
