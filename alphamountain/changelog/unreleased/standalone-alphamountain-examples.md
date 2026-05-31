---
title: Standalone alphaMountain examples
type: breaking
authors:
  - mavam
  - codex
prs:
  - 147
created: 2026-05-31T19:17:14.980497Z
---

The alphaMountain package now ships context update and publishing workflows as
examples instead of installing configured pipelines with package inputs.

Copy the examples into your own deployment and provide the API key, refresh
interval, expiry, and risk threshold directly in the pipeline. This makes the
package safe to install without starting background feed updates automatically.
