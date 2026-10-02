---
title: Expanded OCSF 1.9 field coverage
type: change
authors:
  - mavam
prs:
  - 191
created: 2026-10-02T14:34:35.09218Z
---

Claude Code OCSF events now expose the instrumentation-scope version in `metadata.loggers`, separately from the application and event-schema versions. Scopes without sufficient logger context remain in `unmapped`.
