---
title: Microsoft Entra Conditional Access decisions in OCSF
type: bugfix
authors:
  - mavam
prs:
  - 184
created: 2026-09-02T10:12:24.836951Z
---

Microsoft Entra sign-in events now preserve the Conditional Access decision in
OCSF `authorizations`, keeping policy outcomes distinct from the overall
authentication status.

Thanks to Wouter van Kranenburg for identifying the lost distinction.
