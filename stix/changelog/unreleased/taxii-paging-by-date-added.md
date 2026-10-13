---
title: TAXII paging by date added
type: feature
authors:
  - mavam
prs:
  - 201
created: 2026-10-13T11:43:04.666458Z
---

`stix::taxii::fetch` now walks TAXII 2.1 servers that page without `next` tokens. When a page reports more objects but carries no `next` token, the operator requests the objects added after the `X-TAXII-Date-Added-Last` response header, as the TAXII 2.1 specification describes. Previously, the operator requested the first page of these servers forever.
