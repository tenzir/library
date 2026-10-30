---
title: Source-aware Check Point observation context
type: bugfix
authors:
  - zedoraps
created: 2026-10-28T11:20:32.434902Z
prs:
  - 208
---

Check Point mappings now supply Unknown device type and connection direction values where the source does not report them. Optional device, user, observation-point, and NAT-proxy objects are constructed from reported identities. Unused details retain their source keys in `unmapped`; missing required context remains visible through OCSF validation warnings.
