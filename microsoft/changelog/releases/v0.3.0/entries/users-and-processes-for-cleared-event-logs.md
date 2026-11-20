---
title: Users and processes for cleared event logs
type: bugfix
authors:
  - zedoraps
created: 2026-11-19T15:42:44.696333Z
---

Cleared event logs now name who cleared the log and with which process. Security 1102 and Eventlog 104 now read `UserData/LogFileCleared`, or `EventData` when a collector flattens the section, and Winlogbeat's flattened `user_data` maps the same way. The actor gets:

- The user from `SubjectUserSid` (1102 only), `SubjectUserName`, and `SubjectDomainName`.
- The session from `SubjectLogonId` (1102 only).
- The process ID from `ClientProcessId`, which Windows writes as a decimal number.

Each object appears only when the event names it. `ClientProcessStartKey` stays in `unmapped.EventData`.

Security 1102 read its data from `EventData`, while Windows writes it under `UserData/LogFileCleared`, so the actor of real events had an empty user, session, and process, and the mapping warned about each missing field. Eventlog 104 read the user but discarded the clearing process.

Sigma rules that read `SubjectUserName` or `SubjectUserSid` on 1102 now see a value.
