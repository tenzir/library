---
title: Preserved UDM activity classification
type: bugfix
authors:
  - zedoraps
created: 2026-10-28T11:20:34.106544Z
prs:
  - 208
---

UDM mappings now construct optional endpoint and process context from reported identities and include the required Unknown type and direction values. Known activities and OSINT observations retain their OCSF classification when context or an indicator value is missing. Validation reports the missing required fields as warnings.
