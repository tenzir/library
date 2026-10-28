---
title: Schema-valid OCSF network observations
type: bugfix
authors:
  - zedoraps
created: 2026-10-28T11:20:31.865025Z
prs:
  - 208
---

Route 53 and VPC Flow Log normalization now supplies required connection direction identifiers and retains incomplete endpoint details in unmapped data. Flow observations without either endpoint become Base Events, with the original mapping preserved. Unparseable or absent source events use their observation time when no source clock is available.
