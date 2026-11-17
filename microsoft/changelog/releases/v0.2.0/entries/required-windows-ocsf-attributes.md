---
title: Required OCSF attributes for all Windows events
type: bugfix
authors:
  - zedoraps
prs:
  - 209
created: 2026-08-29T10:25:02.375909Z
---

Every Windows event declares the version and ID of the `win` extension, and an unknown device type for the device and the collector, which OCSF requires.
