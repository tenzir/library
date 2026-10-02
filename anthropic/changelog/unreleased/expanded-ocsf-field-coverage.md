---
title: Expanded OCSF field coverage
type: change
authors:
  - mavam
prs:
  - 191
created: 2026-10-02T14:58:42.149917Z
---

Claude Code OCSF events now expose the instrumentation-scope version in `metadata.loggers`, separately from the application and event-schema versions. Missing scope attributes remain null rather than blocking logger metadata.
