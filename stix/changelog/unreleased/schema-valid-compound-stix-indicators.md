---
title: Preserved compound STIX indicator classification
type: bugfix
authors:
  - zedoraps
created: 2026-10-28T11:20:38.949672Z
prs:
  - 208
---

STIX indicators with compound patterns retain their OSINT Inventory classification and detection pattern. When no single indicator value can be extracted, OCSF validation reports the missing value as a warning. A creator is emitted only when the source identifies one.
