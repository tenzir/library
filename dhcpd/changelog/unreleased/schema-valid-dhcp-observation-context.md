---
title: Preserved DHCP observation context
type: bugfix
authors:
  - zedoraps
created: 2026-10-28T11:20:33.413602Z
prs:
  - 208
---

DHCP mappings now construct device and relay objects when the source identifies them. Unused source context remains in `unmapped`, and known DHCP activities retain their classification when required context is incomplete.
