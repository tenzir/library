---
title: Schema-valid compound STIX indicators
type: bugfix
authors:
  - zedoraps
created: 2026-10-28T11:20:38.949672Z
prs:
  - 208
---

STIX indicators with compound patterns now become Base Events because they have no single indicator value required by OCSF OSINT. Unmappable fields, including the detection pattern, retain their own keys in `unmapped`. A creator is emitted only when the source identifies one.
