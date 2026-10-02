---
title: Expanded OCSF 1.9 field coverage
type: change
authors:
  - mavam
prs:
  - 191
created: 2026-10-02T14:34:35.370771Z
---

BIND OCSF DNS events now expose Recursion Desired and Checking Disabled header flags. The original query-log flag string remains in `unmapped` for EDNS, signature, and COOKIE information; the COOKIE flag is not treated as Checking Disabled.
