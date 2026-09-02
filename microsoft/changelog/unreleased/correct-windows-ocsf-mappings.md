---
title: Correct Windows OCSF mappings
type: bugfix
authors:
  - zedoraps
created: 2026-08-29T10:25:02.375909Z
---

Windows OCSF normalization now uses User Management for account lifecycle events, the plural `users` field for group membership, a source endpoint for Sysmon DNS queries, and Entity Management for directory-object and WMI subscription changes. Defender ASR audit events now produce Detection Findings, and previously unknown Task Scheduler launch and queue events produce Scheduled Job Activity events.

These mappings avoid deprecated OCSF classes and fields, satisfy required OCSF attributes, and replace the confirmed Base Event candidates with event-specific classes and activities.
