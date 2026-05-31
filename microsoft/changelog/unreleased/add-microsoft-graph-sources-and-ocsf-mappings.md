---
title: Add Microsoft Graph sources and OCSF mappings
type: feature
authors:
  - mavam
  - codex
prs:
  - 147
created: 2026-05-27T09:17:24Z
---

Added Microsoft Graph source operators and OCSF mappings for Entra ID sign-ins,
directory audits, Defender alerts and incidents, Identity Protection risk data,
and Intune inventory and compliance data.

The new `microsoft::graph::ocsf::map` operator maps these Graph records to OCSF
Authentication, Account Change, Group Management, Entity Management, Detection
Finding, Incident Finding, Device Inventory Info, Software Inventory Info, and
Compliance Finding events.
