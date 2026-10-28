---
title: Schema-valid Check Point observations
type: bugfix
authors:
  - zedoraps
created: 2026-10-28T11:20:32.434902Z
prs:
  - 208
---

Check Point normalization now supplies required device type and connection direction identifiers. Incomplete user, device, observation-point, and proxy-endpoint details remain in unmapped data instead of producing invalid optional OCSF objects.
