---
title: Okta events in the fitting OCSF classes
type: change
authors:
  - zedoraps
prs:
  - 218
created: 2026-11-24T09:00:00Z
---

Okta events now map to the fitting OCSF class, activity, status, and severity:

- User changes use User Management (3007) instead of the deprecated Account Change (3001).
- Only a request for a session is a Logon.
