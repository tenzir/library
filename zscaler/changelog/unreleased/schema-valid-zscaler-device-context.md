---
title: Schema-valid Zscaler device context
type: bugfix
authors:
  - zedoraps
created: 2026-10-28T11:20:40.751459Z
prs:
  - 208
---

Zscaler normalization now includes the required device type identifier and preserves incomplete devices, owners, and user organizations in unmapped data. Optional context no longer produces OCSF identity-constraint warnings.
