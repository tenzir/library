---
title: Schema-valid OCSF output from CIM
type: bugfix
authors:
  - zedoraps
created: 2026-10-28T11:20:38.499881Z
prs:
  - 208
---

CIM normalization now supplies required file, device, operating-system, database, direction, state, and hash-algorithm identifiers. Incomplete optional identities remain in unmapped data, and file names can be recovered from reported paths. System activities lacking a required actor or device, and File Activities lacking an identifiable file, become Base Events with their original mapping preserved.
