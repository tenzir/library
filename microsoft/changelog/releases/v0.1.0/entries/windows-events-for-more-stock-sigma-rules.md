---
title: Windows events for more stock Sigma rules
type: feature
authors:
  - mavam
prs:
  - 234
created: 2026-11-15T18:35:37.086952Z
---

The `microsoft::windows::ocsf::normalize` operator now maps more Windows events
that stock Sigma rules for Defender, Windows Firewall, AppX deployment, Code
Integrity, and the Security and System logs match on. Previously, these events
became OCSF Base Events, so stock rules for them never matched the normalized
events.

**Microsoft Defender**: Restoring an item from quarantine (EID 1009) and
deleting one (EID 1011) map to Detection Findings with the threat, the affected
files, and the disposition. Deleted malware history (EID 1013), disabled malware
or virus scanning (EIDs 5010 and 5012), blocked tamper attempts (EID 5013), and
an expired antimalware platform (EID 5101) map to Detection Findings like the
existing protection-state events.

**Windows Firewall**: The Windows 11 rule events (EIDs 2071 and 2097 added, 2073
modified, 2052 deleted) map like their earlier counterparts. Setting and profile
changes (EIDs 2002, 2003, 2082, 2083), Group Policy updates and load failures
(EIDs 2008 and 2009), resets to the default configuration (EIDs 2032 and 2060),
and the deletion of all rules (EIDs 2033 and 2059) map to Entity Management
events for the firewall policy, with the modifying user and application.

**AppX deployment**: Deployments that AppLocker or a deployment policy blocked
(EIDs 412, 441, 442, 453, 454) map to failed installs, including EID 441 from
collectors such as Winlogbeat that omit its empty payload. Started deployments
(EID 603) and queued package URIs (EID 854) map to installs without a final
status.

**Code Integrity**: Loads of unsigned, revoked, or non-WHQL images and kernel
modules (EIDs 3001, 3021, 3022, 3032, 3035, 3037, 3083) map to Application
Lifecycle events that describe the load. EID 3032 previously counted as a
block, but Windows reports it when it loads a revoked image.

**Security and System logs**: Created and deleted computer accounts (EIDs 4741
and 4743) map to Account Change, created and removed domain trusts (EIDs 4706
and 4707) map to Entity Management with the trusted domain as the entity, and
services that terminate with an error (EID 7023) map to Windows Service
Activity. Trusted domain policy changes (EID 4716) now also name the trusted
domain.

AppX deployment and Code Integrity events no longer contain empty
`application.url`, `application.product`, or `policy` objects.
