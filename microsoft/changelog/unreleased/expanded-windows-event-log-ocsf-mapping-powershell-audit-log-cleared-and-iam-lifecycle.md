---
title: Expanded Windows Event Log OCSF mapping
type: feature
authors:
  - mavam
prs:
  - 143
  - 147
created: 2026-03-24T13:37:04.933237Z
---

The `microsoft::windows::ocsf::normalize` operator now covers additional high-value Windows Event Log activity:

**PowerShell logging** (EIDs 4100/4103/4104/4105/4106) maps to OCSF Script Activity (1009). EID 4104 (Script Block Logging) sets `severity_id` to Low when AMSI flags the block; EID 4100 (engine error) marks the execution as a failure.

**Audit log cleared** (EID 1102) maps to OCSF Event Log Activity (1008, Clear) with `severity_id` set to High. Clearing the security log is a strong attacker indicator (MITRE ATT&CK T1070.001).

**Scheduled tasks** (EIDs 4698–4702) map create, delete, enable, disable, and update operations to OCSF Scheduled Job Activity (1006).

**Policy changes** (EIDs 4719/4739) map audit-policy and domain-policy updates to OCSF Entity Management (3004).

**Account Change** (EIDs 4720/4722–4726/4740/4767) covers create, enable, disable, delete, password change, password reset, lock, and unlock activities.

**Group Management** (EIDs 4727–4735/4737/4754–4758) covers global, local, and universal security group creation, deletion, updates, and membership changes.

**Group discovery** (EID 4799) maps local group membership enumeration to OCSF Live Evidence Info (5040).

**Remote Desktop denial** (EID 4825) maps rejected post-authentication RDP connections to OCSF RDP Activity (4005).
