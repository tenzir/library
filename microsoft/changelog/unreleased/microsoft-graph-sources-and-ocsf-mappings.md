---
title: Microsoft Graph sources and OCSF mappings
type: feature
authors:
  - mavam
  - codex
prs:
  - 147
created: 2026-05-27T09:17:24Z
---

The Microsoft package can now collect and normalize common Microsoft Graph
security and inventory data.

Use the Graph source operators and `microsoft::ocsf::map` for Entra ID
sign-ins, directory audits, Defender alerts and incidents, Identity Protection
risk data, and Intune inventory and compliance data.

Mapped events cover OCSF Authentication, Account Change, Group Management,
Entity Management, Detection Finding, Incident Finding, Device Inventory Info,
Software Inventory Info, and Compliance Finding classes.
