---
title: Preserved native Zeek observation context
type: bugfix
authors:
  - zedoraps
created: 2026-10-28T11:20:40.274182Z
prs:
  - 208
---

Zeek mappings now construct optional protocol objects from reported identities and retain unused certificate names, encryption details, and other source facts in `unmapped`. Known activities keep their classification when required context is missing, with OCSF validation reporting warnings. Standalone X.509 certificate records use an explicit Base Event mapping and retain their original certificate fields.
