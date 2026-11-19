---
title: HTTP credential stuffing honors custom failure codes
type: bugfix
authors:
  - mavam
prs:
  - 247
created: 2026-11-19T08:38:59.615132Z
---

The `tenzir::detect::http::credential_stuffing` operator now fires for applications that answer failed logins with `200` or a redirect. Previously, adding such a code to `failure_codes` counted every matching response as both a failure and a success, which capped the failure share near 50% and kept the detector below `min_failure_share`. Status codes in `failure_codes` now never count as success:

```tql
tenzir::detect::http::credential_stuffing failure_codes=[200]
```
