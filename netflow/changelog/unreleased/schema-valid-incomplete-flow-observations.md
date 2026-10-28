---
title: Schema-valid incomplete flow observations
type: bugfix
authors:
  - zedoraps
created: 2026-10-28T11:20:35.9532Z
prs:
  - 208
---

NetFlow normalization now preserves incomplete reporter, autonomous-system, proxy-endpoint, and timespan details in unmapped data. Flows that identify neither endpoint become Base Events with their original mapping preserved, including records with an unknown IP version.
