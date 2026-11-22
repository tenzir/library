This release maps Windows account events to OCSF User Management, rebuilds NXLog events like native Windows XML, and names events by their title. Sigma rules on account events and on group members need a Tenzir version whose `sigma` operator reads User Management and `users`.

## 💥 Breaking changes

### Removed Windows Account Change mapping operator

The `microsoft::windows::ocsf::events::account_change` operator is gone because its events now map to User Management. `microsoft::windows::ocsf::normalize` is unaffected; direct callers use `user_management` with the same `windows` and `ocsf` arguments and a User Management `activity_id`.

*By @zedoraps.*

## 🔧 Changes

### Full Windows events from NXLog event XML

Windows events from NXLog Enterprise Edition with `CaptureEventXML TRUE` now normalize from the event XML and map to the same OCSF events as natively collected ones.

- Unnamed event data and `UserData`, such as the client process of a cleared log (104), are now mapped.
- `unmapped.EventData` holds the event data of the XML instead of NXLog's flat copies.
- NXLog's message and metadata stay in `message`, `metadata.loggers`, and `unmapped.NXLog`.

*By @zedoraps.*

### More Windows details in OCSF

More Windows details map to OCSF:

- 4797–4799: the subject as `actor`, and the caller process for 4798/4799.
- Defender 1116/1117: the threat ID in `malware[].uid`, and the platform version in `metadata.product.version`.
- Firewall and IPsec service events 5025, 5030, 5034, 5035, and 5478: Application Lifecycle instead of Base Event. 5033 names the same `Windows Firewall Driver` as 5034 and 5035.
- Account, group, scheduled task, registry, permission, enumeration, and special privilege events, such as 4720, 4728, 4698, 4657, 4670, 4799, and 4672: `status_id` from the audit keywords. Sysmon 12–14 get Success.
- Group membership changes: the common name of a distinguished member name in `users[].name`, such as `carol` for `CN=carol,CN=Users,DC=example,DC=test`, and the full name in `users[].ldap_person.ldap_dn`.
- Scheduled tasks 4698–4702: the command and arguments of the first task action in `job.cmd_line`.
- 4769: the KDC in `dst_endpoint.hostname`, as for 4768. 1100, 1107, and 1108: the `Event Logging Service` as `actor.application.name`.

*By @zedoraps in #261.*

### Windows account events as OCSF User Management

Windows account events now map to OCSF User Management (3007) instead of the deprecated Account Change (3001), and group membership changes list the member in `users` instead of the deprecated `user`.

- 4720/4741 → Create (`1`), 4722 → Enable (`4`), 4723 → Password Change (`8`), 4724 → Password Reset (`9`), 4725 → Disable (`5`), 4726/4743 → Delete (`3`), 4740 → Lock (`6`), 4767 → Unlock (`7`).
- 4728/4729, 4732/4733, 4746/4747, 4751/4752, 4756/4757, and 4761/4762 keep Group Management, with the member in a one-element `users` list.

Sigma rules on these account events and on `MemberName`/`MemberSid` need a Tenzir version whose `sigma` operator reads User Management and `users`.

*By @zedoraps.*

### Windows event titles in message

The OCSF `message` of a Windows event is its title, such as `An account was successfully logged on`, instead of the full rendered message.

- The title is the first line of the rendered message without its closing period or colon. The full message stays in `unmapped.RenderingInfo.Message` when it says more.
- Logon, logoff, Kerberos, NTLM, and other authentication events without a rendered message, such as from Windows Event XML, get the title from Microsoft's event documentation.
- Rendered messages in Windows Event XML keep their line breaks.

*By @zedoraps in #261.*

### Windows levels, keywords, and exact times from NXLog

Windows events from NXLog now carry the level, keywords mask, provider GUID, and activity ID as Windows writes them, and read epoch times exactly.

- `metadata.log_level` comes from `EventType`: `0` for audit events, `1` to `5` for `CRITICAL` through `VERBOSE`.
- The keywords mask is a hex string such as `0x8020000000000000` instead of a signed integer.
- Provider GUIDs and activity IDs are lowercase, and the activity ID becomes `metadata.correlation_uid`.
- Integer `EventTime` and `EventReceivedTime` are read as microseconds since the Unix epoch. NXLog writes them that way with `Exec $EventTime = integer($EventTime); $EventReceivedTime = integer($EventReceivedTime);`.
- String times without a zone are read as UTC.

*By @zedoraps.*

## 🐞 Bug fixes

### Backslashes in PowerShell context values

PowerShell 4100 and 4103 events keep the backslashes in the host application, script path, and user of their context, so `CORP\nora` maps to the user `nora` in the domain `CORP`, and `C:\temp\new.ps1` stays a path.

*By @zedoraps in #256.*

### Defender detection severity

Microsoft Defender detections (1116/1117) now translate the Defender threat severity to the OCSF `severity_id` with the same table as threat (1006/1007) and quarantine (1009/1011) events, and all of them map an undocumented severity to Other.

**Windows writes** (Microsoft Defender 1116):

```xml
<Provider Name="Microsoft-Windows-Windows Defender"/>  <EventID>1116</EventID>
<Data Name="Severity ID">2</Data>          <!-- Defender scale: 1 Low, 2 Moderate, 4 High, 5 Severe -->
<Data Name="Severity Name">Moderate</Data>
```

Threat events (1006/1007) write only the name, such as `<Data Name="Severity">Moderate</Data>`.

**What changes:**

- Detections (1116/1117) with Low (`1`) now get OCSF severity Low (`2`) instead of Informational (`1`).
- Detections (1116/1117) with Moderate (`2`) now get OCSF severity Medium (`3`) instead of Low (`2`).
- Unknown (`0`), High (`4`), and Severe (`5`) map as before.
- Undocumented severities now map to Other (`99`), keeping the name or ID in `severity`, for all Defender events. Detections previously copied the ID; threat and quarantine events used Unknown (`0`).
- Detections without a severity now get Unknown (`0`).

*By @zedoraps.*

### Failure status for denied Windows share access checks and other audit failures

Denied network share access checks and other Windows Security events that Windows logs as audit failures now have status Failure instead of Success.

**Windows writes** (Security 5145, denied):

```xml
<EventID>5145</EventID>
<Keywords>0x8010000000000000</Keywords>  <!-- Audit Failure -->
<Data Name="AccessReason">%%4417:	%%1805</Data>  <!-- WriteData (or AddFile): Not granted -->
```

**What changes:**

- Denied 5145 checks now have status Failure instead of Success, with the reason in `status_detail`, such as `WriteData (or AddFile):	Not granted`.
- Share access (5140) and account mapping (4774) now take their status from the audit keywords: Audit Failure is Failure, Audit Success is Success.
- The audit outcome comes from the Audit Failure and Audit Success bits, so other keyword bits no longer matter. Events with both bits, such as Winlogbeat events that list both `Audit Failure` and `Audit Success`, or with malformed keywords have status Unknown.
- Kerberos TGT and service ticket requests (4768, 4769) and NTLM credential validations (4776) without a result code take their status from the audit keywords instead of Failure.
- Device installations that system policy forbids (6423) now have status Failure instead of Success, with action Denied and disposition Blocked.
- Events without known audit keywords now have status Unknown instead of Success, including handle requests (4656) and object access (4663).
- Events that Windows logs only on success keep status Success: startup (4608), process creation (4688) and exit (4689), session reconnects (4778) and disconnects (4779), and security package loads (4610, 4611, 4614, 4622).

*By @zedoraps.*

### NULL SID no longer becomes a Windows user

The NULL SID (`S-1-0-0`, or `NULL SID` from collectors that translate SIDs) no longer becomes `user.uid` or `actor.user.uid`. 4624/4625 without a subject get no `actor`, and 4625 without a target account gets no `user`.

*By @zedoraps in #261.*

### Process IDs and registry operations from NXLog Community Edition

Windows events from NXLog Community Edition now keep the values that NXLog overwrites or drops.

- Sysmon 1, 3, 5, 11, 12, 13, 22, and 26 get their process IDs again.
- Security 4624, 4657, 4663, 4670, 4688, 4904, 4905, and 4907 get the actor, logon, and parent process IDs.
- Application Error 1000 gets the faulting process ID.
- Sysmon 12 `DeleteKey` and `DeleteValue` map to Delete instead of Create, and `DeleteValue` maps to Registry Value Activity.
- 7045 keeps the service account.
- 104 gets the cleared log and the user, and 1102 gets the subject.
- XML escaping in event data is decoded, so `&lt;unknown process&gt;` becomes `<unknown process>`.
- The overwritten values are read back from the rendered event message. For now, this works only when Windows renders the message in English; on other languages, the values stay missing as before.

*By @zedoraps.*

### Windows event times without rounding errors

Windows event times are rounded to the 100-nanosecond precision that Windows records, so every Tenzir version yields the same value, such as `2024-12-30T09:18:50.491909Z` instead of `2024-12-30T09:18:50.491908999Z`.

*By @zedoraps.*
