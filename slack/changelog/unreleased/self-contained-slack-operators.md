---
title: Self-contained Slack operators
type: change
authors:
  - mavam
  - codex
prs:
  - 147
created: 2026-05-31T19:12:55Z
---

Slack delivery no longer requires a packaged pipeline around the webhook call.

Use `slack::send` directly for message delivery, or `slack::alert` for
structured alert messages. Both operators can post replies into an existing
Slack thread when you provide the thread timestamp.
