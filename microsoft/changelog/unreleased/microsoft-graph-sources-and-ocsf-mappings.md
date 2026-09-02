---
title: Microsoft Graph sources and OCSF mappings
type: feature
authors:
  - mavam
prs:
  - 147
  - 184
created: 2026-05-27T09:17:24Z
---

The Microsoft package can now collect and normalize common Microsoft Graph
security and inventory data. Sign-in events preserve the Microsoft Entra
Conditional Access decision in OCSF `authorizations`, keeping the policy result
distinct from the overall authentication status.

Use the Graph source operators and `microsoft::graph::ocsf::normalize` for Entra ID
sign-ins, directory audits, Defender alerts and incidents, Identity Protection
risk data, and Intune inventory and compliance data.

Thanks to Wouter van Kranenburg for identifying the lost distinction.

Mapped events cover OCSF Authentication, Account Change, Group Management,
Entity Management, Detection Finding, Incident Finding, Device Inventory Info,
Software Inventory Info, and Compliance Finding classes.
