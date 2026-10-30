---
title: Source-aware Okta identities and targets
type: bugfix
authors:
  - zedoraps
created: 2026-10-28T11:20:36.320081Z
prs:
  - 208
---

Okta mappings now identify their logger and authentication service and use reported policy targets as policy identities. Optional users, locations, and URLs are constructed from source identities. Unused organization, ISP, and other source facts remain in `unmapped`. Authentication and account-change observations retain their known classification when the target user is missing; validation reports the missing context as warnings.
