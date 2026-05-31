---
title: Slack webhook delivery for v6
type: breaking
authors:
  - mavam
  - codex
prs:
  - 147
created: 2026-05-31T19:12:55Z
---

Slack webhook delivery now works with the v6 executor through `to_http`.

Use the reusable `slack::send` operator in your own workflow:

```tql
slack::send webhook_url=secret("slack_webhook_url")
```

Pipelines that relied on the old packaged webhook sender should call
`slack::send` explicitly.
