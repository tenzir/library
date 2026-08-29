---
title: Correct Windows OCSF mappings
type: bugfix
authors:
  - zedoraps
created: 2026-08-29T10:25:02.375909Z
---

Windows OCSF normalization now uses User Management for account lifecycle events, the plural `users` field for group membership, a source endpoint for Sysmon DNS queries, and Entity Management for Security EID 5141 directory-object deletions.

These mappings avoid deprecated OCSF classes and fields while satisfying the DNS Activity endpoint requirement.
