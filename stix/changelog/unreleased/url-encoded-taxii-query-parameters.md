---
title: URL-encoded TAXII query parameters
type: bugfix
authors:
  - mavam
prs:
  - 201
created: 2026-10-13T11:49:18.782352Z
---

The `params` of `stix::taxii::fetch` now reach the server URL-encoded. Previously, the operator quoted values with commas, so comma-separated filters such as `"match[type]": "indicator,report"` matched nothing, and it passed `+` in timestamps unencoded.
