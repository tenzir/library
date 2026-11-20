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

### Application hangs as Application Error events

Application hangs (1002) now map to Application Error (6008), like Windows Error Reporting (1001).

| Event | Before                                 | Now                                                             |
| ----- | -------------------------------------- | --------------------------------------------------------------- |
| 1002  | Process Activity · Terminate · Failure | Application Error · General Error, hang type in `status_detail` |

The hung process stays in `unmapped.EventData`:

```tql
status_detail: "Quiesce",
unmapped: {EventData: {AppName: "ExampleViewer.exe", ProcessId: "0x23c8"}},
```

**Why:** Process Activity requires an `actor`, but the event doesn't say whether the user or Windows closed the application.

*By @zedoraps.*

### AppX deployment requesters as actor applications

AppX deployment events now name the requester in `actor.application.name` instead of `actor.process`, and keep the raw value in `unmapped.EventData.CallingProcess`.

| `CallingProcess`             | Before          | Now                                        |
| ---------------------------- | --------------- | ------------------------------------------ |
| `svchost.exe,InstallService` | `actor.process` | `actor.application.name: "InstallService"` |
| `powershell.exe`             | `actor.process` | `actor.application.name: "powershell.exe"` |
| Image with several services  | `actor.process` | No actor                                   |

**What you need to do**

| Rule                                                    | Effect                                                                  | Replacement                   |
| ------------------------------------------------------- | ----------------------------------------------------------------------- | ----------------------------- |
| Windows AppX Deployment Full Trust Package Installation | More alerts: the `svchost.exe,AppReadiness` exclusion no longer applies | Exclude on the unmapped field |

```tql
where class_uid == 6002 and metadata.event_code == "400" and
  application.data.has_full_trust == true and
  not unmapped.EventData.CallingProcess.starts_with("svchost.exe,AppReadiness")
```

**Why:** Windows logs no process ID for the requester, and an OCSF process needs one.

*By @zedoraps.*

### Defender events without a process object

Microsoft Defender detections (1006, 1116, 1117) and attack surface reduction events (1121, 1122) no longer build `actor.process`; the actor keeps the user.

| Field                                | Before                             | Now            |
| ------------------------------------ | ---------------------------------- | -------------- |
| `actor.process`                      | From `Process Name`, without `pid` | Not set        |
| `unmapped.EventData["Process Name"]` | Not set                            | The image path |

**What you need to do**

| Rule                                   | Effect | Replacement              |
| -------------------------------------- | ------ | ------------------------ |
| PSExec and WMI Process Creations Block | Silent | Match the unmapped field |

```tql
where class_uid == 2004 and metadata.event_code == "1121" and
  unmapped.EventData["Process Name"].to_lower().ends_with(r"\wmiprvse.exe")
```

**Why:** Defender logs no process ID, and an OCSF process needs one.

*By @zedoraps.*

### Event Log service start and stop as Event Log Activity

Event Log service starts and stops now map to Event Log Activity, with the logging service in `log_provider`.

| Event | Before                           | Now                        |
| ----- | -------------------------------- | -------------------------- |
| 6005  | Windows Service Activity · Start | Event Log Activity · Start |
| 6006  | Windows Service Activity · Stop  | Event Log Activity · Stop  |

*By @zedoraps.*

### Parameter names for unnamed Windows event data

Unnamed event data from legacy providers, such as Application Error, now uses the names `param1`, `param2`, … for all collectors.

| Collector         | Before                           | Now                   |
| ----------------- | -------------------------------- | --------------------- |
| Windows Event XML | `unmapped.EventData._0`, `_1`, … | `param1`, `param2`, … |
| Winlogbeat        | `param1`, `param2`, …            | Unchanged             |

**What you need to do:** Replace `unmapped.EventData._0` with `unmapped.EventData.param1`, and shift every other index by one.

**Why:** The names match Winlogbeat and the `%1`, `%2` inserts of the provider's message.

*By @zedoraps.*

### Rendered Windows Security message tokens

Security event data now carries the text of message-table tokens, so Windows Event XML, Fluent Bit, and Winlogbeat produce the same event.

| Field                                   | Before                                       | Now                                                  |
| --------------------------------------- | -------------------------------------------- | ---------------------------------------------------- |
| `unmapped.EventData.KernelDebug` (4826) | `%%1843`                                     | `No`                                                 |
| `status_detail` (4625)                  | `%%2313`                                     | `Unknown user name or bad password.`                 |
| `access_list` (4661, 4662)              | `["%%1537"]`                                 | `["DELETE"]`                                         |
| `reg_value.type` (4657)                 | Not set                                      | `REG_EXPAND_SZ`                                      |
| 4719 `entity.policy.data`               | `category_id: "%%8272"`, `changes: "%%8448"` | `category: "System"`, `changes: ["Success removed"]` |
| Winlogbeat 4657 activity                | Unknown                                      | Set, Modify, or Delete                               |

Free-text fields, such as command lines, and unknown tokens stay unchanged.

**What you need to do**

| Query                                           | Effect | Replacement                                       |
| ----------------------------------------------- | ------ | ------------------------------------------------- |
| Tests on a token, such as `%%1843`              | Silent | Test the text, such as `No`                       |
| Tests on 4719 `category_id` or `subcategory_id` | Silent | Test `category` or `subcategory`                  |
| Tests on 4719 `changes` as a string             | Silent | `"Success removed" in entity.policy.data.changes` |

**Why:** Windows Event XML and Fluent Bit report the tokens, while Winlogbeat reports the text.

*By @zedoraps.*

### Service Control Manager state reports as Application Lifecycle events

Service state reports from the Service Control Manager are now Application Lifecycle (6002) events with the service as `application`.

| Event                      | Before                   | Now                                                              |
| -------------------------- | ------------------------ | ---------------------------------------------------------------- |
| 7036 `running`             | Windows Service Activity | Application Lifecycle · Start · Success                          |
| 7036 `stopped`             | Windows Service Activity | Application Lifecycle · Stop · Success                           |
| 7036 other states          | Windows Service Activity | Application Lifecycle · Other (`activity_name` = state)          |
| 7034 crashed               | Windows Service Activity | Application Lifecycle · Stop · Failure                           |
| 7023 terminated with error | Windows Service Activity | Application Lifecycle · Stop · Failure, error in `status_detail` |

Service installations (7045, 4697) and start type changes (7040) remain Windows Service Activity.

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

**Why:** The events name neither the service configuration nor an actor, both of which Windows Service Activity requires.

*By @zedoraps.*

### Sysmon state changes as Application Lifecycle events

Sysmon service state changes (4) now map to Application Lifecycle (6002), with Sysmon and its version in `application`.

| Event          | Before                           | Now                           |
| -------------- | -------------------------------- | ----------------------------- |
| 4 `Started`    | Windows Service Activity · Start | Application Lifecycle · Start |
| 4 `Stopped`    | Windows Service Activity · Stop  | Application Lifecycle · Stop  |
| 4 other states | Windows Service Activity · Stop  | Application Lifecycle · Other |

No Sigma rule is affected: Tenzir's Sigma catalog has no family for `sysmon_status`.

**Why:** The event names neither the service configuration nor an actor, both of which Windows Service Activity requires.

*By @zedoraps.*

### Windows Error Reporting events as Application Error events

Windows Error Reporting events (1001) now map to Application Error (6008), and the report stays in `unmapped.EventData`.

| Event | Before                                 | Now                               |
| ----- | -------------------------------------- | --------------------------------- |
| 1001  | Process Activity · Terminate · Failure | Application Error · General Error |

**Why:** Most reports concern other problems than crashes, such as Windows Update failures, and Application Error 1000 already reports crashes.

*By @zedoraps.*

### Windows Firewall changes without a modifying process

Windows Firewall rule and configuration events (2003–2097) no longer build `actor.process`; the actor keeps the user from `ModifyingUser`.

| Field                                     | Before                                     | Now            |
| ----------------------------------------- | ------------------------------------------ | -------------- |
| `actor.process`                           | From `ModifyingApplication`, without `pid` | Not set        |
| `unmapped.EventData.ModifyingApplication` | Not set                                    | The image path |

**What you need to do**

| Rule                                                                                              | Effect                                                           | Replacement                   |
| ------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------- | ----------------------------- |
| New Firewall Rule Added In Windows Firewall Exception List Via WmiPrvSE.EXE                       | Silent                                                           | Match the unmapped field      |
| A Rule Has Been Deleted From The Windows Firewall Exception List                                  | Silent: its `ModifyingApplication: null` filter drops all events | Filter on the unmapped field  |
| Exclusion-only rules, such as All Rules Have Been Deleted From The Windows Firewall Configuration | More alerts                                                      | Exclude on the unmapped field |

```tql
where metadata.log_name == "Microsoft-Windows-Windows Firewall With Advanced Security/Firewall" and
  metadata.event_code in ["2004", "2071", "2097"] and
  unmapped.EventData.ModifyingApplication.ends_with(r"\WmiPrvSE.exe")
```

**Why:** Windows Firewall logs no process ID, and an OCSF process needs one.

*By @zedoraps.*

## 🐞 Bug fixes

### Actors for Service Control Manager events

Service Control Manager events now have an actor when the event names one.

| Event                                     | Before   | Now                                                         |
| ----------------------------------------- | -------- | ----------------------------------------------------------- |
| 7036 state change                         | No actor | Service Control Manager `pid` and `ptid` in `actor.process` |
| 7040 start type change, 7045 installation | No actor | Header account in `actor.user`                              |

Crashes (7034) and terminations with an error (7023) still have no actor, because the service stopped on its own.

*By @zedoraps.*

### App Control audit and block event fields

App Control audit and block events (3076/3077) now map the file, the loading process, and the signing levels.

| Field                                                                 | Before  | Now                                                       |
| --------------------------------------------------------------------- | ------- | --------------------------------------------------------- |
| `application.name`, `application.data.file_path`                      | Empty   | From `File Name`                                          |
| `actor.process`                                                       | Missing | From `Process Name`                                       |
| `application.data.requested_signing_level`, `validated_signing_level` | Empty   | From `Requested Signing Level`, `Validated Signing Level` |

Sigma rules that read `FileNameBuffer`, `ProcessNameBuffer`, or the signing levels now see these values.

*By @zedoraps.*

### Application crash fields as Windows writes them

Application crashes (1000) now map the values that Windows writes, with or without field names.

| Field                                             | Before               | Now                             |
| ------------------------------------------------- | -------------------- | ------------------------------- |
| `module.file`                                     | Positional data only | Also `ModuleName`, `ModulePath` |
| `module.load_type_id`                             | Not set              | `0` (Unknown)                   |
| `actor.process`                                   | Not set              | The crashed process             |
| `process.pid` without hex letters, such as `2048` | Read as decimal      | Read as hexadecimal             |

*By @zedoraps.*

### AppX deployment errors and packages

Failed AppX deployments (404) now report their error, and events that identify no package have no application.

| Field                           | Before                  | Now                            |
| ------------------------------- | ----------------------- | ------------------------------ |
| `status_detail` of 404          | Not set                 | Error text from `SummaryError` |
| `application` without a package | Built from empty fields | Not set                        |

*By @zedoraps.*

### Decimal Windows access masks

Entity Management events now read a decimal `AccessMask` as decimal.

| `AccessMask`                            | Before                   | Now                     |
| --------------------------------------- | ------------------------ | ----------------------- |
| `16777216` (decimal, some 4674 records) | `access_mask: 376926742` | `access_mask: 16777216` |
| `0x12019f`                              | Hexadecimal              | Hexadecimal             |

Rendered access rights set no `access_mask` and stay in `unmapped.EventData.AccessMask`.

*By @zedoraps.*

### Defender detection evidence without resource prefixes

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

### Device for loaded Boot Configuration Data

Boot Configuration Data load events (4826) now set `entity.device` to the device that logged the event.

**Why:** The entity had no name, ID, or device, which OCSF requires, because the event names the boot configuration only by its settings.

*By @zedoraps.*

### Entities and actors for Windows Security entity events

More Windows Security entity events now identify their entity and actor.

| Event                        | Before             | Now                                                                                         |
| ---------------------------- | ------------------ | ------------------------------------------------------------------------------------------- |
| 4665/4667 client context     | No ID, no actor    | Context ID in `entity.uid`, client in `actor.user`                                          |
| 4870 revoked certificate     | No ID              | Serial number in `entity.uid`                                                               |
| 4902 per-user audit policy   | No ID              | Policy ID in `entity.uid`                                                                   |
| 4931–4933 replication        | No name            | Naming context in `entity.name`; 4932/4933 session in `entity.uid`; 4931/4933 `status_code` |
| 4673 privileged service call | No name            | Service, or else privileges, in `entity.name`                                               |
| 4661, 4670, 4673, 4674       | No `actor.process` | Subject's process in `actor.process`                                                        |

*By @zedoraps.*

### Operating system types for Microsoft Graph devices

Microsoft Graph sign-ins and Intune managed devices now set the operating system type from the reported platform.

| Field                                                                       | Before  | Now                                      |
| --------------------------------------------------------------------------- | ------- | ---------------------------------------- |
| `src_endpoint.os.type_id` (sign-ins), `device.os.type_id` (managed devices) | Not set | Such as `100` (Windows) for `Windows 11` |
| Same, unrecognized platform                                                 | Not set | `99` (Other), name in `os.type`          |

*By @zedoraps.*

### PowerShell host process for script block invocations

PowerShell script block invocation starts and stops (4105/4106) now set `actor.process` to the PowerShell host's `pid` and `ptid`, like script block logging (4104).

*By @zedoraps.*

### Process IDs for Code Integrity actors

Code Integrity events now give the loading process its process and thread ID.

| Field                                       | Before    | Now                                             |
| ------------------------------------------- | --------- | ----------------------------------------------- |
| `actor.process.pid`, `ptid`                 | Not set   | From the event header                           |
| `actor.process` without a header process ID | Path only | Not set; the name stays in `unmapped.EventData` |

**Why:** Code Integrity writes these events in the context of the loading process, and an OCSF process needs a `pid`, `uid`, or `cpid`.

*By @zedoraps.*

### Unknown load type for Sysmon modules

Sysmon image loads (7) and remote thread creations (8) without a start function now set `module.load_type_id` to `0` (Unknown).

**Why:** OCSF requires a module to have a load type or a function name, and Sysmon doesn't report how a module was loaded.

*By @zedoraps.*

### User ID for Entra risky user owners

Microsoft Entra ID risky users now set `resources[].owner.uid` to the risky user's `id`, which Microsoft Graph defines as the ID of the user at risk.

**Why:** The owner had only a display name, which doesn't identify an OCSF user.

*By @zedoraps.*

### Users and processes for cleared event logs

Cleared event logs now name who cleared the log and with which process.

| Event         | Before                       | Now                                                |
| ------------- | ---------------------------- | -------------------------------------------------- |
| Security 1102 | Empty user, session, process | `actor.user`, `actor.session`, `actor.process.pid` |
| Eventlog 104  | User only                    | `actor.user`, `actor.process.pid`                  |

```tql
actor: {
  user: {name: "lmorgan", domain: "EXAMPLE"},
  session: {uid_alt: "0x5d2e71"},
  process: {pid: 6212},
},
```

Sigma rules that read `SubjectUserName` or `SubjectUserSid` on 1102 now see a value.

**Why:** The mapping read `EventData`, while Windows writes the data under `UserData/LogFileCleared`.

*By @zedoraps.*
