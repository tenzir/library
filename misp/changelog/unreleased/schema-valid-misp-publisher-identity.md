---
title: Schema-valid MISP publisher identity
type: bugfix
authors:
  - zedoraps
created: 2026-10-28T11:20:35.33156Z
prs:
  - 208
---

MISP normalization now identifies the publisher as an application. Source organizations remain in unmapped data when no user identifier is available, preventing organization-only users and name-only processes from violating OCSF identity constraints.
