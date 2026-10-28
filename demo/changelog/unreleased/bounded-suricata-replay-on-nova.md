---
title: Bounded Suricata replay on Nova
type: bugfix
authors:
  - zedoraps
created: 2026-10-28T11:20:33.11554Z
prs:
  - 200
---

Suricata replay now terminates when a downstream limit has consumed enough events on Nova. DNS and TLS sampling continues to reduce frequent event types while allowing bounded demo pipelines to complete.
