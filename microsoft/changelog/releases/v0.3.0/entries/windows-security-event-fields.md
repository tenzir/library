---
title: Windows Security event fields
type: bugfix
authors:
  - zedoraps
created: 2026-11-18T10:40:11.340169Z
---

More Windows Security entity events now identify their entity and actor, Entity Management events read a decimal `AccessMask` as decimal, and cleared event logs now name who cleared the log and with which process.

| Event | Before | Now |
|---|---|---|
| 4665/4667 client context | No ID, no actor | Context ID in `entity.uid`, client in `actor.user` |
| 4870 revoked certificate | No ID | Serial number in `entity.uid` |
| 4902 per-user audit policy | No ID | Policy ID in `entity.uid` |
| 4931–4933 replication | No name | Naming context in `entity.name`; 4932/4933 session in `entity.uid`; 4931/4933 `status_code` |
| 4673 privileged service call | No name | Service, or else privileges, in `entity.name` |
| 4661, 4670, 4673, 4674 | No `actor.process` | Subject's process in `actor.process` |
| 4826 Boot Configuration Data load | No name, ID, or device | Device that logged the event in `entity.device` |
| Entity Management, decimal `AccessMask` `16777216` (some 4674 records) | `access_mask: 376926742` | `access_mask: 16777216` |
| Entity Management, `AccessMask` `0x12019f` | Hexadecimal | Hexadecimal |
| Security 1102 log cleared | Empty user, session, process | `actor.user`, `actor.session`, `actor.process.pid` |
| Eventlog 104 log cleared | User only | `actor.user`, `actor.process.pid` |

Rendered access rights set no `access_mask` and stay in `unmapped.EventData.AccessMask`.

```tql
actor: {
  user: {name: "lmorgan", domain: "EXAMPLE"},
  session: {uid_alt: "0x5d2e71"},
  process: {pid: 6212},
},
```

Sigma rules that read `SubjectUserName` or `SubjectUserSid` on 1102 now see a value.

**Why:** The 4826 entity had no name, ID, or device, which OCSF requires, because the event names the boot configuration only by its settings. For cleared logs, the mapping read `EventData`, while Windows writes the data under `UserData/LogFileCleared`.
