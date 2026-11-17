---
title: Defender attack surface reduction events and detections
type: bugfix
authors:
  - zedoraps
prs:
  - 209
created: 2026-08-29T10:25:02.375909Z
---

Attack surface reduction events (1121 block, 1122 audit) read the fields that Defender actually writes. They report the rule as the analytic with its name, and the acting process, the user, and the targeted file. Defender detections classify the malware by its category, and an absent action no longer becomes an Other disposition.
