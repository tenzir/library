---
title: Okta parsing, polling, and mapping operators
type: breaking
authors:
  - mavam
  - zedoraps
prs:
  - 147
  - 218
created: 2026-05-31T19:12:55Z
---

The `okta` package changes these operators:

- `okta::read` replaces `okta::clean`.
- `okta::fetch` takes `token` and `scheme` instead of `bearer_token` and `swss_token`, and keeps polling without `every`.
- `okta::ocsf::event::user_management` replaces `okta::ocsf::event::account_change`.
