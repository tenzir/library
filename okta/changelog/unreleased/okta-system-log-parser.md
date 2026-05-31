---
title: Okta System Log parser
type: breaking
authors:
  - mavam
  - codex
prs:
  - 147
created: 2026-05-31T19:12:55Z
---

Replace the removed Okta clean operator with an `okta::read` parser that
normalizes System Log input from any byte source.
