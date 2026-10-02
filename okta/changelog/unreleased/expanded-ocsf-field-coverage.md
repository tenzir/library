---
title: Expanded OCSF 1.9 field coverage
type: change
authors:
  - mavam
prs:
  - 191
created: 2026-10-02T14:34:35.619802Z
---

Okta OCSF events now expose client device IDs, names, and OS versions on the client endpoint, including finding evidence. Existing endpoint identities are not overwritten, and unsupported Base Event device context remains in `unmapped`.
