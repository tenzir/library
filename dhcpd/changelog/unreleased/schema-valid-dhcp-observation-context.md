---
title: Schema-valid DHCP observation context
type: bugfix
authors:
  - zedoraps
created: 2026-10-28T11:20:33.413602Z
prs:
  - 208
---

DHCP normalization now retains incomplete device and relay details in unmapped data when the source does not identify those objects. This prevents optional context from violating OCSF identity constraints.
