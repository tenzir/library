---
title: Source-aware Zscaler device context
type: bugfix
authors:
  - zedoraps
created: 2026-10-28T11:20:40.751459Z
prs:
  - 208
---

Zscaler mappings now include the required Unknown device type when a device is identified. Unused device-owner and department facts retain their original source keys in `unmapped`, without creating unidentified devices or organization objects.
