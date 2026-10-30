---
title: Preserved incomplete flow observations
type: bugfix
authors:
  - zedoraps
created: 2026-10-28T11:20:35.9532Z
prs:
  - 208
---

NetFlow mappings now construct reporter, endpoint, autonomous-system, NAT-proxy, and timespan objects from the source values needed to identify them. Unused ports, addresses, and other facts retain their original source keys in `unmapped`.

Flow records retain Network Activity classification when endpoint identities are missing; validation emits warnings. Source records that do not describe flows use an explicit Base Event mapping. Selecting one IP address preserves distinct unselected address-family values.
