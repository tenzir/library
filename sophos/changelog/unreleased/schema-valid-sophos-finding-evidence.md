---
title: Schema-valid Sophos finding evidence
type: bugfix
authors:
  - zedoraps
created: 2026-10-28T11:20:38.20508Z
prs:
  - 208
---

Sophos normalization now supplies required file type identifiers in events and finding evidence. Evidence processes without a reported process identifier remain in evidence data, preserving their details without creating an invalid OCSF process.
