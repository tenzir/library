---
title: Expanded OCSF 1.9 field coverage
type: change
authors:
  - mavam
prs:
  - 191
created: 2026-10-02T14:34:35.377229Z
---

Windows OCSF events now expose Kerberos service identities, ticket flags and complete PKINIT certificates; RDP session IDs; faulting modules and process-start times; and account display names and alternate IDs. Service start/type values are translated to OCSF enums, with unknown flag combinations preserved as Other. Sentinels, incomplete certificates, and vendor-specific context remain in `unmapped`.
