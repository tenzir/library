---
title: Schema-valid native Zeek observations
type: bugfix
authors:
  - zedoraps
created: 2026-10-28T11:20:40.274182Z
prs:
  - 208
---

Zeek normalization now supplies required direction and file identifiers while preserving incomplete optional protocol objects in unmapped data. Observations without identities required by their activity class become Base Events with their original mapping preserved.
