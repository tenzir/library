---
title: Sophos SIEM collection for v6
type: breaking
authors:
  - mavam
  - codex
prs:
  - 147
created: 2026-05-31T19:12:55Z
---

Sophos collection now uses native v6 HTTP pipelines instead of embedded Python
collectors.

Use the Sophos fetch operators with `from_http` pagination, then map alerts,
detections, endpoint records, and SIEM events with the package OCSF operators.
This makes Sophos onboarding easier to inspect, customize, and run in the v6
executor.
