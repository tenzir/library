This release corrects how the Microsoft package maps Windows events whose test fixtures did not match real records, such as application crashes, Windows Error Reporting, Service Control Manager, App Control, Defender, and AppX events. Security events now carry the text of their message tokens, so Windows Event XML, Fluent Bit, and Winlogbeat produce the same events. The package also stops building OCSF objects that the events cannot fill: processes that Windows names without a process ID stay in unmapped, and Sysmon state changes and application hangs move to classes that their data supports. Three event mapping operators are gone, and some Sigma rules that read the affected fields no longer match; the entries name the replacements. Microsoft Graph devices now report their operating system type.

## 💥 Breaking changes

### Removed Windows event mapping operators

Three Windows event mapping operators are gone because their events now map to other OCSF classes. If you call them directly, switch to their replacements:

- `microsoft::windows::ocsf::events::application_crash_report` (Windows Error Reporting 1001) is now `microsoft::windows::ocsf::events::error_report`.
- `microsoft::windows::ocsf::events::eventlog_start` (6005) is now `microsoft::windows::ocsf::events::eventlog_service_state` with `activity_id=6`.
- `microsoft::windows::ocsf::events::eventlog_stop` (6006) is now `microsoft::windows::ocsf::events::eventlog_service_state` with `activity_id=7`.

The replacements take the same positional arguments, `windows` and `ocsf`. Pipelines that call `microsoft::windows::ocsf::normalize` need no change.

*By @zedoraps.*

## 🔧 Changes

### Application hangs as Application Error events

Application hangs (1002) now map to Application Error (6008) instead of Process Activity, like Windows Error Reporting events (1001). The hang type, such as `Quiesce`, maps to `status_detail`.

Process Activity requires an `actor`, but the event doesn't say who closed the hung application, the user or Windows, so `ocsf_cast` warned about every hang.

Application Error has no process object, so the hung process stays in `unmapped.EventData` under its source names, such as `AppName`, `ProcessId`, `StartTime`, and `ExeFileName`. Tenzir's Sigma catalog maps no rules for the Application log, so no Sigma rule depends on the previous class.

*By @zedoraps.*

### AppX deployment requesters as actor applications

AppX deployment events now map the requester to `actor.application.name` instead of `actor.process`:

- A process that hosts exactly one service maps to that service, such as `AppReadiness`.
- A process that hosts no service maps to its image, such as `powershell.exe`.
- A process that hosts several services doesn't tell which one requested the deployment, so the event has no actor.

The raw value stays in `unmapped.EventData.CallingProcess`.

Windows reports the requester in `CallingProcess` as an image name followed by the services it hosts, such as `svchost.exe,AppReadiness`, and logs no process ID. An OCSF process needs a `pid`, `uid`, or `cpid`, so `ocsf_cast` warned about these events. OCSF defines `actor.application` as the client application or service that initiated the activity.

Tenzir's Sigma catalog reads `CallingProcess` from `actor.process.path`, so Sigma rules that test it now see no value. SigmaHQ's *Windows AppX Deployment Full Trust Package Installation* uses it only to exclude `sysprep.exe` and `svchost.exe,AppReadiness`, so it now also matches these deployments. To keep the exclusion, match the unmapped field:

```tql
where class_uid == 6002 and metadata.event_code == "400" and
  application.data.has_full_trust == true and
  not unmapped.EventData.CallingProcess.starts_with("svchost.exe,AppReadiness")
```

*By @zedoraps.*

### Defender events without a process object

Microsoft Defender detections (1006, 1116, 1117) and attack surface reduction events (1121, 1122) no longer build `actor.process` from `Process Name`. The image path stays in `unmapped.EventData["Process Name"]`, and the actor keeps the user when Defender names one.

Defender names the process only by its image path and logs no process ID. An OCSF process needs a `pid`, `uid`, or `cpid`, so `ocsf_cast` warned about these events.

Tenzir's Sigma catalog reads `ProcessName` from `actor.process.path`, so Sigma rules that test it now see no value, and SigmaHQ's *PSExec and WMI Process Creations Block* no longer matches. Match the unmapped field instead:

```tql
where class_uid == 2004 and metadata.event_code == "1121" and
  unmapped.EventData["Process Name"].to_lower().ends_with(r"\wmiprvse.exe")
```

*By @zedoraps.*

### Event Log service start and stop as Event Log Activity

Event Log service starts (6005) and stops (6006) now map to Event Log Activity with the Start and Stop activities instead of Windows Service Activity. Like the other Event Log service events, they name the logging service in `log_provider`.

*By @zedoraps.*

### Parameter names for unnamed Windows event data

Unnamed event data now uses the names `param1`, `param2`, and so on, for all collectors. Legacy providers, such as Application Error and Windows Error Reporting, write event data without field names. Windows Event XML parsing names these fields `_0`, `_1`, and so on, while Winlogbeat names them `param1`, `param2`, and so on, which match the `%1`, `%2` inserts of the provider's message.

If your queries read `unmapped.EventData._0`, read `unmapped.EventData.param1` instead, and shift every other index by one.

*By @zedoraps.*

### Rendered Windows Security message tokens

The Windows normalizer now replaces the message-table tokens in Security events with the text that Windows renders, such as `No` for `%%1843`. Windows Event XML and Fluent Bit report the tokens, while Winlogbeat reports the text, so all collectors now produce the same event.

Only the event data fields that hold tokens change. Free-text fields, such as command lines and paths, stay unchanged even if they contain a token. Values that list several tokens, such as access rights, access reasons, or `UserAccountControl` flags, render each token and keep their separators, GUIDs, and SDDL strings. The texts are the en-US message strings of `msobjs.dll`. Unknown tokens stay unchanged, and Winlogbeat records rendered in another language keep that language.

For example, the Boot Configuration Data settings of 4826 now read `unmapped.EventData.KernelDebug: "No"`, so detections for test signing, kernel debugging, or disabled integrity checks can match on `"Yes"`. The rendered text also improves mapped fields:

- 4625 failure reasons in `status_detail`, such as `Unknown user name or bad password.`
- 4657 registry value types in `reg_value.type_id` and `reg_value.type`, such as `REG_EXPAND_SZ`. Unknown value types stay in `unmapped.EventData`.
- 4661 and 4662 access rights in `access_list`, such as `Read Property`.
- 4662 and 5136 directory operations in `entity.data.operation`, such as `Value Added`.
- 4719 audit policy categories, subcategories, and changes in `entity.policy.data`.

The 4719 fields in `entity.policy.data` have new names because they now hold names instead of tokens: `category_id` is now `category`, and `subcategory_id` is now `subcategory`. `changes` is now a list, such as `["Success Added", "Failure added"]`, instead of a comma-separated string. Update queries and detections that use the previous names. The subcategory GUID remains the policy's `uid`.

Winlogbeat records now also map 4657 registry operations to their activity instead of Unknown, and keep rendered access rights that contain spaces as one entry in `access_list`.

*By @zedoraps.*

### Service Control Manager state reports as Application Lifecycle events

Service Control Manager state reports now map to Application Lifecycle (6002) instead of Windows Service Activity: service state changes (7036), unexpected terminations (7034), and terminations with an error (7023). Like Windows Firewall 5024, the service is the `application`, with its display name in `application.name` and `type: "Windows Service"`:

- 7036 maps `running` to Start and `stopped` to Stop, with status Success. Other states, including localized ones such as `arrêté`, map to Other with the state as `activity_name`.
- 7034 and 7023 map to Stop with status Failure. The error message of 7023 stays in `status_detail`, including a `%%21`-style token from the system message table. The termination count of 7034 stays in `unmapped.EventData.param2`, because OCSF `count` counts aggregated events.

The events name neither the service configuration nor a process or account that caused the change. Windows Service Activity requires both a `win_service` with service details and an `actor`, so `ocsf_cast` warned about these events. Service installations (7045 and 4697) and start type changes (7040) remain Windows Service Activity.

Tenzir's Sigma catalog reads the System log service family only from Windows Service Activity, so SigmaHQ's *Windows Defender Threat Detection Service Disabled*, *Important Windows Service Terminated Unexpectedly*, *Important Windows Service Terminated With Error*, and *Windows Service Terminated With Error* no longer match. Query Application Lifecycle instead:

```tql
// Windows Defender Threat Detection Service Disabled
where (metadata.product.name == "Service Control Manager"
  and metadata.event_code == "7036"
  and application.name in ["Windows Defender Antivirus Service", "Service antivirus Microsoft Defender"]
  and (activity_id == 4 or activity_name == "arrêté"))
```

```tql
// Important Windows Service Terminated Unexpectedly
where (metadata.product.name == "Service Control Manager"
  and metadata.event_code == "7034"
  and application.name.match_regex("Message Queuing"))
```

```tql
// Important Windows Service Terminated With Error; drop the name test for
// Windows Service Terminated With Error.
where (metadata.product.name == "Service Control Manager"
  and metadata.event_code == "7023"
  and application.name.match_regex(" Antivirus| Firewall|Application Guard|BitLocker Drive Encryption Service|Encrypting File System|Microsoft Defender|Threat Protection|Windows Event Log"))
```

The 7034 and 7023 rules also match the service key name, such as `WinDefend`, which Windows writes as UTF-16 hex in the event's binary data. Only collectors that ship this data, such as Winlogbeat, report it, in `unmapped.EventData.Binary`, so that alternative works only for them. Windows Event XML parsing drops the binary data, so match those records on `application.name`.

*By @zedoraps.*

### Sysmon state changes as Application Lifecycle events

Sysmon service state changes (4) now map to Application Lifecycle (6002) with the Start or Stop activity, and the Sysmon service with its version in `application`.

The event names neither the service configuration nor a process or account that changed the state. Windows Service Activity requires both a `win_service` with service details and an `actor`, so `ocsf_cast` warned about these events.

Tenzir's Sigma catalog has no family for the `sysmon_status` category, so no Sigma rule depends on the previous class.

*By @zedoraps.*

### Windows Error Reporting events as Application Error events

Windows Error Reporting events (1001) now map to Application Error instead of Process Activity, which claimed a process termination. The report's event name and problem signature stay in `unmapped`.

Most of these reports concern other problems, such as Windows Update failures or missing drivers, and Application Error 1000 already reports application crashes.

*By @zedoraps.*

### Windows Firewall changes without a modifying process

Windows Firewall rule and configuration events (2003–2097) no longer build `actor.process` from `ModifyingApplication`. The path stays in `unmapped.EventData.ModifyingApplication`, and the actor keeps the modifying user from `ModifyingUser`.

Windows Firewall names the modifying application only by its image path and logs no process ID. An OCSF process needs a `pid`, `uid`, or `cpid`, so `ocsf_cast` warned about these events.

Tenzir's Sigma catalog reads `ModifyingApplication` from `actor.process.path`, so Sigma rules that test it now see no value:

- *New Firewall Rule Added In Windows Firewall Exception List Via WmiPrvSE.EXE* no longer matches.
- *A Rule Has Been Deleted From The Windows Firewall Exception List* filters out every event through its `ModifyingApplication: null` filter.
- Rules that only exclude applications, such as *All Rules Have Been Deleted From The Windows Firewall Configuration*, now also match the excluded applications.

Match the application on the unmapped field instead:

```tql
where metadata.log_name == "Microsoft-Windows-Windows Firewall With Advanced Security/Firewall" and
  metadata.event_code in ["2004", "2071", "2097"] and
  unmapped.EventData.ModifyingApplication.ends_with(r"\WmiPrvSE.exe")
```

*By @zedoraps.*

## 🐞 Bug fixes

### Actors for Service Control Manager events

Service Control Manager events now have an actor when the event names one:

- Service state changes (7036) name the Service Control Manager process.
- Start type changes (7040) and service installations (7045) name the account from the event header.

Service crashes (7034) and terminations with an error (7023) still have no actor, because the service stopped on its own.

*By @zedoraps.*

### App Control audit and block event fields

App Control audit and block events (3076/3077) now map the file, the loading process, and the signing levels. Windows reports them in `File Name`, `Process Name`, `Requested Signing Level`, and `Validated Signing Level`.

Sigma rules that read `FileNameBuffer`, `ProcessNameBuffer`, or the signing levels now see these values.

*By @zedoraps.*

### Application crash fields as Windows writes them

Application crashes (1000) now map the values that Windows writes, with or without field names. The faulting process and module are filled in, including the module from `ModuleName` and `ModulePath`. The crashed process is also the actor, and the faulting module has an unknown load type. Hexadecimal process IDs and exception codes without letters keep their value.

*By @zedoraps.*

### AppX deployment errors and packages

Failed AppX deployments (404) now report the error text in `status_detail`. Events that identify no package have no application.

*By @zedoraps.*

### Decimal Windows access masks

Entity Management events now read a decimal `AccessMask` as decimal. Some 4674 records log the mask in decimal, such as `16777216` for `ACCESS_SYSTEM_SECURITY`, which the mapping read as hexadecimal and turned into `access_mask: 376926742`. A mask with a `0x` prefix is hexadecimal, and digits alone are decimal.

Rendered access rights set no `access_mask` and stay in `unmapped.EventData.AccessMask`.

*By @zedoraps.*

### Defender detection evidence without resource prefixes

Microsoft Defender detections (1116/1117) now list each detected file on disk once in `evidences`, without the resource prefix that Defender writes in `Path`, such as `file:_`:

- Container files (`containerfile:_`) and downloads (`webfile:_`) count as files. For a download, the evidence is the local path, without the URL and the process details.
- An archive member, such as `file:_C:\x.zip->(Zip:y.exe)`, becomes its container, `C:\x.zip`, because OCSF has no field for archive members.
- Other resources, such as registry keys, aren't evidence. A detection without a file has no `evidences`.

The complete list stays in `unmapped.EventData.Path`.

*By @zedoraps.*

### Device for loaded Boot Configuration Data

Boot Configuration Data load events (4826) now identify the managed entity by the device that logged the event, in `entity.device`.

The event names the boot configuration only by its settings, so the entity had no name, ID, or device, which OCSF requires, and `ocsf_cast` warned about every such event.

*By @zedoraps.*

### Entities and actors for Windows Security entity events

More Windows Security entity events now identify their entity and actor:

- Authorization Manager client contexts (4665/4667) use the client context ID and the client account.
- Revoked certificates (4870) use the serial number.
- Per-user audit policy tables (4902) use the policy ID.
- Directory replication events (4931–4933) use the naming context and the replication session. Replication results (4931/4933) also set `status_code` and `status_id`.
- Privileged service calls (4673) name the called service, or the exercised privileges when the event names no service.

Events that report the subject's process, such as 4661, 4670, 4673, and 4674, now carry it in `actor.process`.

*By @zedoraps.*

### Operating system types for Microsoft Graph devices

Microsoft Graph sign-ins and Intune managed devices now set the operating system type, such as Windows, iOS, or Android, from the reported platform name. An unrecognized platform maps to Other with the reported name.

*By @zedoraps.*

### PowerShell host process for script block invocations

PowerShell script block invocation starts and stops (4105/4106) now name the PowerShell host process in `actor.process`, like script block logging (4104).

*By @zedoraps.*

### Process IDs for Code Integrity actors

Code Integrity events now give the loading process in `actor.process` its process and thread ID. Code Integrity writes these events in the context of the loading process, so the event header carries its ID.

Before, `actor.process` had only a path, and `ocsf_cast` warned that an OCSF process needs a `pid`, `uid`, or `cpid`. Events without a header process ID keep the process name in `unmapped.EventData`.

*By @zedoraps.*

### Unknown load type for Sysmon modules

Sysmon image loads (7) now set `module.load_type_id` to 0 (Unknown), and remote thread creations (8) do so when Sysmon names no start function. A remote thread with a start function, such as `CtrlRoutine`, keeps it in `module.function_name` and needs no load type.

Sysmon doesn't report how a module was loaded, and OCSF requires a module to have a load type or a function name, so `ocsf_cast` warned about these events.

*By @zedoraps.*

### User ID for Entra risky user owners

Microsoft Entra ID risky users now identify the owner of the affected account by the user's ID, in `resources[].owner.uid`. Microsoft Graph defines the risky user's `id` as the ID of the user at risk.

Before, the owner had only the display name, which doesn't identify an OCSF user, and `ocsf_cast` warned about every risky user.

*By @zedoraps.*

### Users and processes for cleared event logs

Cleared event logs now name who cleared the log and with which process. Security 1102 and Eventlog 104 now read `UserData/LogFileCleared`, or `EventData` when a collector flattens the section, and Winlogbeat's flattened `user_data` maps the same way. The actor gets:

- The user from `SubjectUserSid` (1102 only), `SubjectUserName`, and `SubjectDomainName`.
- The session from `SubjectLogonId` (1102 only).
- The process ID from `ClientProcessId`, which Windows writes as a decimal number.

Each object appears only when the event names it. `ClientProcessStartKey` stays in `unmapped.EventData`.

Security 1102 read its data from `EventData`, while Windows writes it under `UserData/LogFileCleared`, so the actor of real events had an empty user, session, and process, and the mapping warned about each missing field. Eventlog 104 read the user but discarded the clearing process.

Sigma rules that read `SubjectUserName` or `SubjectUserSid` on 1102 now see a value.

*By @zedoraps.*
