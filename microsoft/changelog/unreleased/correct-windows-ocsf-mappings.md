---
title: Correct Windows OCSF mappings
type: bugfix
authors:
  - zedoraps
prs:
  - 183
  - 209
created: 2026-08-29T10:25:02.375909Z
---

Windows OCSF normalization now uses User Management for account lifecycle events, the plural `users` field for group membership, and Entity Management for directory-object and WMI subscription changes. Defender ASR audit events now produce Detection Findings, and previously unknown Task Scheduler launch and queue events produce Scheduled Job Activity events.

These mappings avoid deprecated OCSF classes and fields, satisfy required OCSF attributes, and replace the confirmed Base Event candidates with event-specific classes and activities.

ASR audit findings preserve executable evidence when no process identifier is available. WMI bindings are identified by their reported filter and consumer, and scheduler status events use the scheduler account reported in the event header.

Account lifecycle events retain real display names and principal names in `user.display_name` and `user.uid_alt`, while Windows message-resource tokens remain unmapped.
