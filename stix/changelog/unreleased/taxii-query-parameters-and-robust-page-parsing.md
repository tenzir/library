---
title: TAXII query parameters and robust page parsing
type: change
authors:
  - mavam
prs:
  - 196
created: 2026-10-09T12:57:52.26169Z
---

`stix::taxii::fetch` now takes TAXII query parameters such as `added_after`, `limit`, and `match[type]` as a `params` record, and a `paginate_delay` for servers with rate limits. It also parses pages whose multi-byte characters span two network chunks, and accepts pages without objects.
