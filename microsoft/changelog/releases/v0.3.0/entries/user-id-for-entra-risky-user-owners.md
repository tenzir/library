---
title: User ID for Entra risky user owners
type: bugfix
authors:
  - zedoraps
created: 2026-11-19T01:07:32.699525Z
---

Microsoft Entra ID risky users now set `resources[].owner.uid` to the risky user's `id`, which Microsoft Graph defines as the ID of the user at risk.

**Why:** The owner had only a display name, which doesn't identify an OCSF user.
