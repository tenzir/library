---
title: Incomplete TAXII pagination detection
type: bugfix
authors:
  - mavam
prs:
  - 202
created: 2026-10-20T18:57:32.513979Z
---

`stix::taxii::fetch` now fails a walk when a page advertises more results but provides neither a usable `next` token nor a date-added continuation. Previously, the walk could silently finish with an incomplete collection, causing downstream snapshot updates to remove valid data.
