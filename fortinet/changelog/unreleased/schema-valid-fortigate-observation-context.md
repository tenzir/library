---
title: Source-aware FortiGate observation context
type: bugfix
authors:
  - zedoraps
created: 2026-10-28T11:20:33.79058Z
prs:
  - 208
---

FortiGate mappings now supply required Unknown type identifiers during object construction. Device and analytic objects use reported identities. Country names that cannot populate an OCSF location retain their original source keys in `unmapped`, including when network context becomes finding evidence.
