---
title: Preserved CIM activity classification and context
type: bugfix
authors:
  - zedoraps
created: 2026-10-28T11:20:38.499881Z
prs:
  - 208
---

CIM mappings now supply required Unknown type and direction values during construction and recover file names from reported paths. Optional processes, users, endpoints, and devices use their source identities; unused facts retain their CIM keys in `unmapped`.

Known System and File Activities retain their class and activity when required actor, device, or file context is missing. OCSF validation reports warnings instead of reclassifying these observations as Base Events.
