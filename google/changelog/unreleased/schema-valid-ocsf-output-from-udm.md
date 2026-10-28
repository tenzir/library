---
title: Schema-valid OCSF output from UDM
type: bugfix
authors:
  - zedoraps
created: 2026-10-28T11:20:34.106544Z
prs:
  - 208
---

UDM normalization now includes required device, file, module, and connection identifiers and preserves incomplete endpoints in unmapped data. OSINT observations without a required indicator value become Base Events with their original mapping preserved.
