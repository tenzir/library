---
title: Schema-valid Okta identities and targets
type: bugfix
authors:
  - zedoraps
created: 2026-10-28T11:20:36.320081Z
prs:
  - 208
---

Okta normalization now identifies its logger and authentication service and derives policy identities from the reported target. Incomplete owner, location, and URL details remain in unmapped data. Authentication and account-change observations without a required user become Base Events with their original mapping preserved.
