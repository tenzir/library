---
title: Network logons without a logon process
type: bugfix
authors:
  - zedoraps
created: 2026-11-19T00:22:07.40595Z
---

Authentication events for logons without a local process, such as Kerberos or NTLM network logons, no longer carry a `logon_process` object. Windows reports `ProcessId: 0x0` and `ProcessName: -` for them and names the security package, such as `Kerberos` or `NtLmSsp`, as `LogonProcessName`. An OCSF process needs a `pid`, `uid`, or `cpid`, so `ocsf_cast` warned about these events. The name now stays in `unmapped.EventData.LogonProcessName`, and the package remains in `auth_protocol`. Logons with a local process keep `logon_process` with the process ID and image.

Sigma rules that match `LogonProcessName` on network logons, such as the `NtLmSsp` branch of SigmaHQ's *Pass the Hash Activity 2*, run against `logon_process.name` and no longer match these events. Match them on `auth_protocol_id` and `logon_type_id` instead, for example:

```tql
where class_uid == 3002 and logon_type_id == 3 and auth_protocol_id == 1
```
