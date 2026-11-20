---
title: Windows Security event fields
type: bugfix
authors:
  - zedoraps
created: 2026-11-18T10:40:11.340169Z
---

More Windows Security entity events now identify their entity and actor, Entity Management events read a decimal `AccessMask` as decimal, and cleared event logs now name who cleared the log and with which process.

#### Entity names and IDs

**Windows writes** (one field per event that identifies the entity):

```xml
<EventID>4665</EventID>  <Data Name="ClientLogonId">{11111111-2222-3333-4444-555555555555}</Data>  <!-- client context ID -->
                         <Data Name="ClientName">WS01</Data>  <Data Name="ClientDomain">EXAMPLE</Data>
<EventID>4870</EventID>  <Data Name="CertificateSerialNumber">6100000003c2a1f9e0b7d5a4ce000000000003</Data>
<EventID>4902</EventID>  <Data Name="PuaPolicyId">0x5a1e</Data>
<EventID>4931</EventID>  <Data Name="NamingContext">DC=ForestDnsZones,DC=example,DC=test</Data>  <Data Name="StatusCode">0</Data>
<EventID>4673</EventID>  <Data Name="Service">-</Data>  <Data Name="PrivilegeList">SeLoadDriverPrivilege</Data>
```

**OCSF before → now:**

| Event | Before | Now |
|---|---|---|
| 4665/4667 client context | No ID, no actor (warning) | Context ID in `entity.uid`, client in `actor.user` |
| 4870 revoked certificate | No ID (warning) | Serial number in `entity.uid` |
| 4902 per-user audit policy | No ID (warning) | Policy ID in `entity.uid` |
| 4931–4933 replication | No name (warning) | Naming context in `entity.name`; 4932/4933 session in `entity.uid`; 4931/4933 `status_code` and `status_id` |
| 4673 privileged service call | No name (warning) | Service, or else privileges, in `entity.name` |

**Why:** each of these events identifies its entity in a field of its own, which the mapping didn't read, so the entity had no name or ID, which OCSF requires. Most 4673 records write the service as `-`, so the exercised privileges name the call.

#### Subject process

**Windows writes** (Security 4674; 4661, 4670, and 4673 alike):

```xml
<EventID>4674</EventID>
<Data Name="ProcessId">0x12c</Data>                                 <!-- subject's process -->
<Data Name="ProcessName">C:\Windows\System32\notepad.exe</Data>
```

**OCSF before → now:**

| Event | Before | Now |
|---|---|---|
| 4661, 4670, 4673, 4674 | No `actor.process`; values in `unmapped.EventData` | Subject's process in `actor.process`, such as `pid: 300` |

**Why:** these events name the process that the subject used, with its ID, so it belongs to the actor.

#### Boot Configuration Data

**Windows writes** (Security 4826):

```xml
<EventID>4826</EventID>  <Computer>WS04</Computer>  <!-- device that loaded it -->
<Data Name="KernelDebug">%%1843</Data>             <!-- settings only -->
<Data Name="TestSigning">%%1843</Data>
```

**OCSF before → now:**

| Event | Before | Now |
|---|---|---|
| 4826 Boot Configuration Data load | No name, ID, or device (warning) | Device that logged the event in `entity.device` |

**Why:** the event describes the loaded Boot Configuration Data only by its settings, with no name or ID. It belongs to the device that logs the event, so that device identifies the entity, which OCSF requires to have a name, ID, or device.

#### Access masks

**Windows writes** (Security 4674 and 4656):

```xml
<EventID>4674</EventID>  <Data Name="AccessMask">16777216</Data>  <!-- decimal, in some 4674 records -->
<EventID>4656</EventID>  <Data Name="AccessMask">0x12019f</Data>  <!-- hexadecimal -->
```

**OCSF before → now:**

| Event | Before | Now |
|---|---|---|
| Entity Management, decimal `AccessMask` `16777216` (some 4674 records), from collectors that ship it as text, such as Winlogbeat | `access_mask: 376926742` | `access_mask: 16777216` |
| Entity Management, decimal `AccessMask` `16777216`, Windows Event XML | `access_mask: 16777216` | `access_mask: 16777216` |
| Entity Management, `AccessMask` `0x12019f` | Hexadecimal | Hexadecimal |

Rendered access rights set no `access_mask` and stay in `unmapped.EventData.AccessMask`.

**Why:** Windows writes most access masks in hexadecimal with `0x`, but some 4674 records in decimal. The mapping read every mask as hexadecimal, which went wrong whenever the mask arrived as text.

#### Cleared event logs

**Windows writes** (Security 1102; Eventlog 104 alike, without the SID and logon ID):

```xml
<EventID>1102</EventID>
<UserData><LogFileCleared>                                   <!-- not EventData -->
  <SubjectUserName>lmorgan</SubjectUserName>  <SubjectLogonId>0x5d2e71</SubjectLogonId>
  <ClientProcessId>6212</ClientProcessId>                    <!-- decimal -->
</LogFileCleared></UserData>
```

**OCSF before → now:**

| Event | Before | Now |
|---|---|---|
| Security 1102 log cleared | Empty user, session, process (warnings) | `actor.user`, `actor.session`, `actor.process.pid` |
| Eventlog 104 log cleared | User only | `actor.user`, `actor.process.pid` |

```tql
actor: {
  user: {name: "lmorgan", domain: "EXAMPLE"},
  session: {uid_alt: "0x5d2e71"},
  process: {pid: 6212},
},
```

Sigma rules that read `SubjectUserName` or `SubjectUserSid` on 1102 now see a value.

**Why:** for cleared logs, the mapping read `EventData`, while Windows writes the data under `UserData/LogFileCleared`. Windows writes `ClientProcessId` in decimal, such as `6212`, which the 1102 mapping read as hexadecimal.
