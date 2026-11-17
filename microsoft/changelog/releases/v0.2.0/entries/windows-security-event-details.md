---
title: Accurate details of Windows security events
type: bugfix
authors:
  - zedoraps
prs:
  - 209
created: 2026-08-29T10:25:02.375909Z
---

- Process creation (4688) names the creator as `actor.process`.
- System access changes (4717, 4718) list the granted or removed rights in `privileges`.
- Account lockouts (4740) report the caller computer in `src_endpoint` instead of `user.domain`.
- NTLM validation (4776) names the validating domain controller and the package of unknown protocols.
- Share access (5140) no longer reports a file without a name, and Remote Desktop sessions are inbound connections.
- Security package events (4610, 4611, 4614, 4622) identify the LSA process by its PID and the account that registered a trusted logon process, and report an unknown load type for the package.
- Registry value changes (4657) no longer report Windows message tokens as value types.
- Account lifecycle events keep real display names and principal names, while Windows message tokens stay in `unmapped`.
