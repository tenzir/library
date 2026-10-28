---
title: Nova-compatible authenticated requests
type: bugfix
authors:
  - zedoraps
created: 2026-10-28T11:20:34.396804Z
prs:
  - 200
---

Jev enrichment now works with Nova when authentication is optional. Requests without an API key no longer require a configured secret; requests with an API key continue to use authenticated HTTP.
