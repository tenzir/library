---
title: Repeat counts, session IDs, and empty fields in PAN-OS events
type: change
authors:
  - zedoraps
created: 2026-11-27T13:34:20.624676Z
---

The OCSF mapping represents three PAN-OS values more accurately:

- The repeat count becomes `count`, instead of staying in `unmapped`.
- Session ID 0, which PAN-OS writes when it created no session, no longer becomes `connection_info.uid` and stays in `unmapped`.
- Empty PAN-OS fields no longer appear as null fields in `unmapped`.
