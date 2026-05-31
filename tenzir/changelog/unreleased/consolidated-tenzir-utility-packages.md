---
title: Consolidated Tenzir utility packages
type: breaking
authors:
  - mavam
  - codex
prs:
  - 147
created: 2026-05-31T19:12:55Z
---

OSINT enrichment and OCSF trimming utilities now live in the `tenzir` package.

Use the new namespaced utility operators in your pipelines:

```tql
tenzir::osint::enrich
tenzir::trim
```

Installations that used the previous utility packages should switch to the
corresponding `tenzir::*` operator names.
