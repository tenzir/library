---
title: User ID for Entra risky user owners
type: bugfix
authors:
  - zedoraps
created: 2026-11-19T01:07:32.699525Z
---

Microsoft Entra ID risky users now identify the owner of the affected account by the user's ID, in `resources[].owner.uid`. Microsoft Graph defines the risky user's `id` as the ID of the user at risk.

Before, the owner had only the display name, which doesn't identify an OCSF user, and `ocsf_cast` warned about every risky user.
