---
title: Schema-valid firewall observation context
type: bugfix
authors:
  - zedoraps
created: 2026-10-28T11:20:37.695418Z
prs:
  - 208
---

Firewall normalization now preserves incomplete location, owner, proxy-endpoint, firewall-rule, policy, and evidence-user details in unmapped data. Empty evidence actors are omitted after incomplete users are preserved. Optional context no longer produces OCSF identity-constraint warnings.
