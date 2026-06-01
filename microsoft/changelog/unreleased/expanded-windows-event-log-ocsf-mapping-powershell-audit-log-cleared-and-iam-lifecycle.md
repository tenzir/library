---
title: 'Expanded Windows Event Log OCSF mapping: PowerShell, audit log cleared, and
  IAM lifecycle'
type: feature
authors:
  - mavam
  - claude
prs:
  - 143
  - 147
created: 2026-03-24T13:37:04.933237Z
---

The `microsoft::windows::ocsf::map` operator now covers five additional Windows Event Log categories:

**PowerShell logging** (EIDs 4100/4103/4104/4105/4106) maps to OCSF Script Activity (1009). EID 4104 (Script Block Logging) sets `severity_id` to Low when AMSI flags the block; EID 4100 (engine error) marks the execution as a failure.

**Audit log cleared** (EID 1102) maps to OCSF Event Log Activity (1008, Clear) with `severity_id` set to High — clearing the security log is a strong attacker indicator (MITRE ATT&CK T1070.001).

**Account Change** (EIDs 4720/4722–4726) replaces the previous create-only handler and now covers the full lifecycle: create, enable, disable, delete, password change, and password reset, using the correct OCSF 3001 activity IDs throughout.

**Group Management** (EIDs 4727–4734/4754–4757) replaces the previous add-member-only handler and now covers global, local, and universal security group create, delete, add member, and remove member.
