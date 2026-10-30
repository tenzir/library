---
title: Required OCSF device types and fallback times
type: bugfix
authors:
  - zedoraps
created: 2026-10-28T11:20:34.713271Z
prs:
  - 208
---

Kunai normalization now supplies the required device type identifier. Unparsed observations without a source timestamp use their observation time, so the Base Event fallback includes the required OCSF time.
