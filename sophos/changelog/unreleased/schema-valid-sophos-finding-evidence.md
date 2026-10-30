---
title: Preserved Sophos finding evidence
type: bugfix
authors:
  - zedoraps
created: 2026-10-28T11:20:38.20508Z
prs:
  - 208
---

Sophos mappings now supply required file type identifiers when constructing finding evidence. Process names and command lines without a reported process identifier remain in the original source fields under `unmapped`. Display names without user identity are retained without creating unidentified owners.
