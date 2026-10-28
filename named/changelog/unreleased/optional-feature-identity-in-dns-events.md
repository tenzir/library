---
title: Optional feature identity in DNS events
type: bugfix
authors:
  - zedoraps
created: 2026-10-28T11:20:35.625457Z
prs:
  - 208
---

DNS normalization now omits an empty product-feature object when the source reports no feature name. This prevents optional product metadata from violating OCSF identity constraints.
