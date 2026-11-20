---
title: Users and processes for cleared event logs
type: bugfix
authors:
  - zedoraps
created: 2026-11-19T15:42:44.696333Z
---

Cleared event logs now name who cleared the log and with which process.

| Event | Before | Now |
|---|---|---|
| Security 1102 | Empty user, session, process | `actor.user`, `actor.session`, `actor.process.pid` |
| Eventlog 104 | User only | `actor.user`, `actor.process.pid` |

```tql
actor: {
  user: {name: "lmorgan", domain: "EXAMPLE"},
  session: {uid_alt: "0x5d2e71"},
  process: {pid: 6212},
},
```

Sigma rules that read `SubjectUserName` or `SubjectUserSid` on 1102 now see a value.

**Why:** The mapping read `EventData`, while Windows writes the data under `UserData/LogFileCleared`.
