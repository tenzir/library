This release maps Windows events the way real records write them and stops building OCSF objects that the events can't fill.

| Area                    | What changes                                                                                                                                                                                                                                |
| ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Message tokens          | Security event data carries rendered text instead of `%%` tokens, and unnamed event data is `param1`, `param2`, … for all collectors.                                                                                                       |
| Class changes           | Service Control Manager and Sysmon state reports, application hangs, Windows Error Reporting, and Event Log service starts and stops move to classes that their data supports.                                                              |
| Objects no longer built | Defender, Windows Firewall, and AppX events no longer build `actor.process` without a process ID. Some Sigma rules go silent or match more; the entries give replacements.                                                                  |
| Bug fixes               | Application crashes, App Control, AppX errors, Code Integrity, cleared logs, Defender evidence, Security entity events and access masks, PowerShell, Sysmon modules, and Microsoft Graph devices and risky users map more fields correctly. |
| Removed operators       | `application_crash_report`, `eventlog_start`, and `eventlog_stop` are gone; `microsoft::windows::ocsf::normalize` needs no change.                                                                                                          |
| Test data               | The test fixtures use synthetic records instead of records from public datasets.                                                                                                                                                            |

## 💥 Breaking changes

### Removed Windows event mapping operators

Three operators under `microsoft::windows::ocsf::events::` are gone because their events now map to other OCSF classes.

| Removed operator                  | Replacement                                   |
| --------------------------------- | --------------------------------------------- |
| `application_crash_report` (1001) | `error_report`                                |
| `eventlog_start` (6005)           | `eventlog_service_state` with `activity_id=6` |
| `eventlog_stop` (6006)            | `eventlog_service_state` with `activity_id=7` |

**What you need to do:** Nothing if you call `microsoft::windows::ocsf::normalize`. If you call a removed operator directly, switch to its replacement, which takes the same positional arguments, `windows` and `ocsf`.

*By @zedoraps.*

## 🔧 Changes

### Application hangs and error reports as Application Error

Windows Error Reporting events (1001) and application hangs (1002) now map to Application Error (6008).

| Event                        | Before                                 | Now                                                             |
| ---------------------------- | -------------------------------------- | --------------------------------------------------------------- |
| 1001 Windows Error Reporting | Process Activity · Terminate · Failure | Application Error · General Error                               |
| 1002 application hang        | Process Activity · Terminate · Failure | Application Error · General Error, hang type in `status_detail` |

The report and the hung process stay in `unmapped.EventData`:

```tql
status_detail: "Quiesce",
unmapped: {EventData: {AppName: "ExampleViewer.exe", ProcessId: "0x23c8"}},
```

**Why:** Most error reports concern other problems than crashes, such as Windows Update failures, and Application Error 1000 already reports crashes. Process Activity requires an `actor`, but a hang event doesn't say whether the user or Windows closed the application.

*By @zedoraps.*

### No process objects without a process ID

Microsoft Defender, Windows Firewall, and AppX deployment events no longer build `actor.process`, and keep the raw value in `unmapped.EventData` instead.

| Source                                                                                  | Before                                                     | Now                                                                                                    |
| --------------------------------------------------------------------------------------- | ---------------------------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| Defender detections (1006, 1116, 1117) and attack surface reduction events (1121, 1122) | `actor.process` from `Process Name`, without `pid`         | Image path in `unmapped.EventData["Process Name"]`; the actor keeps the user                           |
| Windows Firewall rule and configuration events (2003–2097)                              | `actor.process` from `ModifyingApplication`, without `pid` | Image path in `unmapped.EventData.ModifyingApplication`; the actor keeps the user from `ModifyingUser` |
| AppX deployment, `CallingProcess` `svchost.exe,InstallService`                          | `actor.process`                                            | `actor.application.name: "InstallService"`                                                             |
| AppX deployment, `CallingProcess` `powershell.exe`                                      | `actor.process`                                            | `actor.application.name: "powershell.exe"`                                                             |
| AppX deployment, image with several services                                            | `actor.process`                                            | No actor                                                                                               |

AppX deployment events name the requester in `actor.application.name` and keep the raw value in `unmapped.EventData.CallingProcess`. Before, `unmapped.EventData` had neither `Process Name` nor `ModifyingApplication`.

**What you need to do**

| Rule                                                                                              | Source           | Effect                                                                  | Replacement                   |
| ------------------------------------------------------------------------------------------------- | ---------------- | ----------------------------------------------------------------------- | ----------------------------- |
| PSExec and WMI Process Creations Block                                                            | Defender         | Silent                                                                  | Match the unmapped field      |
| New Firewall Rule Added In Windows Firewall Exception List Via WmiPrvSE.EXE                       | Windows Firewall | Silent                                                                  | Match the unmapped field      |
| A Rule Has Been Deleted From The Windows Firewall Exception List                                  | Windows Firewall | Silent: its `ModifyingApplication: null` filter drops all events        | Filter on the unmapped field  |
| Exclusion-only rules, such as All Rules Have Been Deleted From The Windows Firewall Configuration | Windows Firewall | More alerts                                                             | Exclude on the unmapped field |
| Windows AppX Deployment Full Trust Package Installation                                           | AppX deployment  | More alerts: the `svchost.exe,AppReadiness` exclusion no longer applies | Exclude on the unmapped field |

<details>
<summary>Replacement queries</summary>

```tql
// PSExec and WMI Process Creations Block
where class_uid == 2004 and metadata.event_code == "1121" and
  unmapped.EventData["Process Name"].to_lower().ends_with(r"\wmiprvse.exe")
```

```tql
// New Firewall Rule Added In Windows Firewall Exception List Via WmiPrvSE.EXE
where metadata.log_name == "Microsoft-Windows-Windows Firewall With Advanced Security/Firewall" and
  metadata.event_code in ["2004", "2071", "2097"] and
  unmapped.EventData.ModifyingApplication.ends_with(r"\WmiPrvSE.exe")
```

```tql
// Windows AppX Deployment Full Trust Package Installation
where class_uid == 6002 and metadata.event_code == "400" and
  application.data.has_full_trust == true and
  not unmapped.EventData.CallingProcess.starts_with("svchost.exe,AppReadiness")
```

</details>

**Why:** Defender and Windows Firewall log no process ID, nor does Windows for the AppX requester, and an OCSF process needs one.

*By @zedoraps.*

### Same Windows event data from every collector

Security event data now carries the text of message-table tokens, and unnamed event data from legacy providers, such as Application Error, now uses the names `param1`, `param2`, … for all collectors, so Windows Event XML, Fluent Bit, and Winlogbeat produce the same event.

| Field                                   | Before                                       | Now                                                  |
| --------------------------------------- | -------------------------------------------- | ---------------------------------------------------- |
| `unmapped.EventData.KernelDebug` (4826) | `%%1843`                                     | `No`                                                 |
| `status_detail` (4625)                  | `%%2313`                                     | `Unknown user name or bad password.`                 |
| `access_list` (4661, 4662)              | `["%%1537"]`                                 | `["DELETE"]`                                         |
| `reg_value.type` (4657)                 | Not set                                      | `REG_EXPAND_SZ`                                      |
| 4719 `entity.policy.data`               | `category_id: "%%8272"`, `changes: "%%8448"` | `category: "System"`, `changes: ["Success removed"]` |
| Winlogbeat 4657 activity                | Unknown                                      | Set, Modify, or Delete                               |
| Unnamed event data, Windows Event XML   | `unmapped.EventData._0`, `_1`, …             | `param1`, `param2`, …                                |
| Unnamed event data, Winlogbeat          | `param1`, `param2`, …                        | Unchanged                                            |

Free-text fields, such as command lines, and unknown tokens stay unchanged.

**What you need to do**

| Query                                           | Effect | Replacement                                                                                          |
| ----------------------------------------------- | ------ | ---------------------------------------------------------------------------------------------------- |
| Tests on a token, such as `%%1843`              | Silent | Test the text, such as `No`                                                                          |
| Tests on 4719 `category_id` or `subcategory_id` | Silent | Test `category` or `subcategory`                                                                     |
| Tests on 4719 `changes` as a string             | Silent | `"Success removed" in entity.policy.data.changes`                                                    |
| Tests on `unmapped.EventData._0`                | Silent | Replace `unmapped.EventData._0` with `unmapped.EventData.param1`, and shift every other index by one |

**Why:** Windows Event XML and Fluent Bit report the tokens, while Winlogbeat reports the text. The parameter names match Winlogbeat and the `%1`, `%2` inserts of the provider's message.

*By @zedoraps.*

### Service and log service events in fitting classes

Service state reports from the Service Control Manager and Sysmon service state changes (4) now map to Application Lifecycle (6002), and Event Log service starts and stops now map to Event Log Activity.

| Event                                              | Before                           | Now                                                              |
| -------------------------------------------------- | -------------------------------- | ---------------------------------------------------------------- |
| Service Control Manager 7036 `running`             | Windows Service Activity         | Application Lifecycle · Start · Success                          |
| Service Control Manager 7036 `stopped`             | Windows Service Activity         | Application Lifecycle · Stop · Success                           |
| Service Control Manager 7036 other states          | Windows Service Activity         | Application Lifecycle · Other (`activity_name` = state)          |
| Service Control Manager 7034 crashed               | Windows Service Activity         | Application Lifecycle · Stop · Failure                           |
| Service Control Manager 7023 terminated with error | Windows Service Activity         | Application Lifecycle · Stop · Failure, error in `status_detail` |
| Sysmon 4 `Started`                                 | Windows Service Activity · Start | Application Lifecycle · Start                                    |
| Sysmon 4 `Stopped`                                 | Windows Service Activity · Stop  | Application Lifecycle · Stop                                     |
| Sysmon 4 other states                              | Windows Service Activity · Stop  | Application Lifecycle · Other                                    |
| Event Log 6005                                     | Windows Service Activity · Start | Event Log Activity · Start                                       |
| Event Log 6006                                     | Windows Service Activity · Stop  | Event Log Activity · Stop                                        |

Application Lifecycle events carry the service, or Sysmon and its version, in `application`. Event Log Activity events carry the logging service in `log_provider`. Service installations (7045, 4697) and start type changes (7040) remain Windows Service Activity.

```tql
class_uid: 6002,
activity_name: "Start",
status_id: 1,
application: {name: "ExampleUpdate", type: "Windows Service"},
```

**What you need to do**

Tenzir's Sigma catalog reads the System log service family only from Windows Service Activity, so these SigmaHQ rules no longer match:

| Rule                                               | Effect | Replacement            |
| -------------------------------------------------- | ------ | ---------------------- |
| Windows Defender Threat Detection Service Disabled | Silent | 7036, Defender stopped |
| Important Windows Service Terminated Unexpectedly  | Silent | 7034, service name     |
| Important Windows Service Terminated With Error    | Silent | 7023, service name     |
| Windows Service Terminated With Error              | Silent | 7023                   |

```tql
// Windows Defender Threat Detection Service Disabled
where (metadata.product.name == "Service Control Manager"
  and metadata.event_code == "7036"
  and application.name in ["Windows Defender Antivirus Service", "Service antivirus Microsoft Defender"]
  and (activity_id == 4 or activity_name == "arrêté"))
```

<details>
<summary>More replacement queries</summary>

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

</details>

The 7034 and 7023 rules can also match the service key name in `unmapped.EventData.Binary`, but only collectors that ship it, such as Winlogbeat, report it.

No Sigma rule is affected by the Sysmon change: Tenzir's Sigma catalog has no family for `sysmon_status`.

**Why:** The Service Control Manager and Sysmon events name neither the service configuration nor an actor, both of which Windows Service Activity requires.

*By @zedoraps.*

## 🐞 Bug fixes

### Application crashes and Code Integrity

Application crashes (1000) now map the values that Windows writes, with or without field names, Code Integrity events now give the loading process its process and thread ID, and App Control audit and block events (3076/3077) now map the file, the loading process, and the signing levels.

| Event                 | Field                                                                 | Before               | Now                                                       |
| --------------------- | --------------------------------------------------------------------- | -------------------- | --------------------------------------------------------- |
| 1000 crash            | `module.file`                                                         | Positional data only | Also `ModuleName`, `ModulePath`                           |
| 1000 crash            | `module.load_type_id`                                                 | Not set              | `0` (Unknown)                                             |
| 1000 crash            | `actor.process`                                                       | Not set              | The crashed process                                       |
| 1000 crash            | `process.pid` without hex letters, such as `2048`                     | Read as decimal      | Read as hexadecimal                                       |
| Code Integrity        | `actor.process.pid`, `ptid`                                           | Not set              | From the event header                                     |
| Code Integrity        | `actor.process` without a header process ID                           | Path only            | Not set; the name stays in `unmapped.EventData`           |
| 3076/3077 App Control | `application.name`, `application.data.file_path`                      | Empty                | From `File Name`                                          |
| 3076/3077 App Control | `actor.process`                                                       | Missing              | From `Process Name`                                       |
| 3076/3077 App Control | `application.data.requested_signing_level`, `validated_signing_level` | Empty                | From `Requested Signing Level`, `Validated Signing Level` |

Sigma rules that read `FileNameBuffer`, `ProcessNameBuffer`, or the signing levels now see these values.

**Why:** Code Integrity writes these events in the context of the loading process, and an OCSF process needs a `pid`, `uid`, or `cpid`.

*By @zedoraps.*

### Defender detection evidence

Microsoft Defender detections (1116/1117) now list each detected file on disk once in `evidences`, instead of one file holding the whole `Path` with its resource prefixes.

| Resource in `Path`                               | Evidence now               |
| ------------------------------------------------ | -------------------------- |
| `file:_C:\x.exe`, `containerfile:_C:\x.zip`      | The file                   |
| `file:_C:\x.zip->(Zip:y.exe)`                    | The container, `C:\x.zip`  |
| `webfile:_C:\x.exe`, followed by URL and process | The local path, `C:\x.exe` |
| `regkey:_…` and other resources                  | None                       |

```tql
evidences: [
  {file: {path: "C:\\Users\\rchen\\Downloads\\tools.zip", name: "tools.zip", type_id: 1}},
  {file: {path: "C:\\Users\\rchen\\Downloads\\setup.exe", name: "setup.exe", type_id: 1}},
],
```

The complete list stays in `unmapped.EventData.Path`.

*By @zedoraps.*

### Microsoft Graph devices and risky users

Microsoft Graph sign-ins and Intune managed devices now set the operating system type from the reported platform, and Microsoft Entra ID risky users now identify their owner.

| Source                                           | Field                                                                       | Before  | Now                                                                                |
| ------------------------------------------------ | --------------------------------------------------------------------------- | ------- | ---------------------------------------------------------------------------------- |
| Sign-ins, managed devices                        | `src_endpoint.os.type_id` (sign-ins), `device.os.type_id` (managed devices) | Not set | Such as `100` (Windows) for `Windows 11`                                           |
| Sign-ins, managed devices, unrecognized platform | Same                                                                        | Not set | `99` (Other), name in `os.type`                                                    |
| Entra ID risky users                             | `resources[].owner.uid`                                                     | Not set | The risky user's `id`, which Microsoft Graph defines as the ID of the user at risk |

**Why:** The owner had only a display name, which doesn't identify an OCSF user.

*By @zedoraps.*

### Services, AppX, PowerShell, and Sysmon

Service Control Manager events now have an actor when the event names one, failed AppX deployments report their error, PowerShell script block invocations name their host process, and Sysmon modules get a load type.

| Event                                                                   | Field                 | Before                  | Now                                                                  |
| ----------------------------------------------------------------------- | --------------------- | ----------------------- | -------------------------------------------------------------------- |
| Service Control Manager 7036 state change                               | `actor.process`       | No actor                | Service Control Manager `pid` and `ptid`                             |
| Service Control Manager 7040 start type change, 7045 installation       | `actor.user`          | No actor                | Header account                                                       |
| AppX deployment 404 failure                                             | `status_detail`       | Not set                 | Error text from `SummaryError`                                       |
| AppX deployment without a package                                       | `application`         | Built from empty fields | Not set                                                              |
| PowerShell 4105/4106 script block invocation start and stop             | `actor.process`       | Not set                 | PowerShell host's `pid` and `ptid`, like script block logging (4104) |
| Sysmon 7 image load, 8 remote thread creation, without a start function | `module.load_type_id` | Not set                 | `0` (Unknown)                                                        |

Service Control Manager crashes (7034) and terminations with an error (7023) still have no actor, because the service stopped on its own.

**Why:** OCSF requires a module to have a load type or a function name, and Sysmon doesn't report how a module was loaded.

*By @zedoraps.*

### Windows Security event fields

More Windows Security entity events now identify their entity and actor, Entity Management events read a decimal `AccessMask` as decimal, and cleared event logs now name who cleared the log and with which process.

| Event                                                                  | Before                       | Now                                                                                         |
| ---------------------------------------------------------------------- | ---------------------------- | ------------------------------------------------------------------------------------------- |
| 4665/4667 client context                                               | No ID, no actor              | Context ID in `entity.uid`, client in `actor.user`                                          |
| 4870 revoked certificate                                               | No ID                        | Serial number in `entity.uid`                                                               |
| 4902 per-user audit policy                                             | No ID                        | Policy ID in `entity.uid`                                                                   |
| 4931–4933 replication                                                  | No name                      | Naming context in `entity.name`; 4932/4933 session in `entity.uid`; 4931/4933 `status_code` |
| 4673 privileged service call                                           | No name                      | Service, or else privileges, in `entity.name`                                               |
| 4661, 4670, 4673, 4674                                                 | No `actor.process`           | Subject's process in `actor.process`                                                        |
| 4826 Boot Configuration Data load                                      | No name, ID, or device       | Device that logged the event in `entity.device`                                             |
| Entity Management, decimal `AccessMask` `16777216` (some 4674 records) | `access_mask: 376926742`     | `access_mask: 16777216`                                                                     |
| Entity Management, `AccessMask` `0x12019f`                             | Hexadecimal                  | Hexadecimal                                                                                 |
| Security 1102 log cleared                                              | Empty user, session, process | `actor.user`, `actor.session`, `actor.process.pid`                                          |
| Eventlog 104 log cleared                                               | User only                    | `actor.user`, `actor.process.pid`                                                           |

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

*By @zedoraps.*
