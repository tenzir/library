---
title: Windows account events as OCSF User Management
type: change
authors:
  - zedoraps
created: 2026-11-20T19:45:56.225751Z
---

Windows account lifecycle events now map to OCSF User Management (3007) instead of the deprecated Account Change (3001), and group membership changes put the member into `users` instead of the deprecated `user`.

**Windows writes** (Security 4740 and 4728):

```xml
<EventID>4740</EventID>
<Data Name="TargetUserName">kpatel</Data>
<Data Name="TargetSid">S-1-5-21-1111111111-2222222222-3333333333-2104</Data>

<EventID>4728</EventID>
<Data Name="MemberName">CN=backdoor_svc,CN=Users,DC=corp,DC=local</Data>
<Data Name="MemberSid">S-1-5-21-3107921522-2185401913-891411500-1500</Data>
<Data Name="TargetUserName">DomainAdmins</Data>
```

**What changes:**

- 4720 (user created) and 4741 (computer account created): Account Change Create → User Management Create (`1`).
- 4722 (enabled): Account Change Enable → User Management Enable (`4`).
- 4723 (password change attempt): Account Change Password Change → User Management Password Change (`8`).
- 4724 (password reset attempt): Account Change Password Reset → User Management Password Reset (`9`).
- 4725 (disabled): Account Change Disable → User Management Disable (`5`).
- 4726 (user deleted) and 4743 (computer account deleted): Account Change Delete → User Management Delete (`3`).
- 4740 (locked out): Account Change Lock → User Management Lock (`6`).
- 4767 (unlocked): Account Change Unlock → User Management Unlock (`7`).
- 4728/4729, 4732/4733, 4746/4747, 4751/4752, 4756/4757, and 4761/4762 (member added or removed): Group Management keeps the class and activity, but the member moves from `user` to a one-element `users` list.

The target account, actor, session, lockout source, and unmapped fields stay as they were.

**What you need to do:** Update queries that select these events by class or read the group member:

```tql
// Before
where class_uid == 3001
// After
where class_uid == 3007 and activity_id in [1, 3, 4, 5, 6, 7, 8, 9]

// Before
where class_uid == 3006 and user.uid == "S-1-5-21-3107921522-2185401913-891411500-1500"
// After
where class_uid == 3006 and "S-1-5-21-3107921522-2185401913-891411500-1500" in users.map(x => x.uid)
```

Sigma rules for `product: windows` and `service: security` no longer match these account events, and rules that read `MemberName` or `MemberSid` no longer match group membership changes, because the `sigma` operator still looks for them in Account Change and in the Group Management `user`. Rules on the group itself, such as `EventID: 4732` with `TargetSid: S-1-5-32-544`, still match. Until the `sigma` operator catches up, run such a rule as TQL. For example, a rule that selects `EventID: 4741` with `TargetUserName|endswith: '$'` becomes:

```tql
where class_uid == 3007 and metadata.event_code == "4741" and user.name.ends_with("$")
```

A rule that selects `EventID: 4728` with `MemberSid` becomes:

```tql
where class_uid == 3006 and metadata.event_code == "4728" and "S-1-5-21-3107921522-2185401913-891411500-1500" in users.map(x => x.uid)
```
