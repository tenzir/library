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

**Why:** the removed operators built Process Activity and Windows Service Activity events. Windows Error Reporting 1001 now maps to Application Error and Event Log 6005 and 6006 to Event Log Activity, which the replacements build.

**What you need to do:** Nothing if you call `microsoft::windows::ocsf::normalize`. If you call a removed operator directly, switch to its replacement, which takes the same positional arguments, `windows` and `ocsf`.

*By @zedoraps.*

## 🔧 Changes

### Application hangs and error reports as Application Error

Windows Error Reporting events (1001) and application hangs (1002) now map to Application Error (6008).

#### Windows Error Reporting

**Windows writes** (Windows Error Reporting 1001, values without names):

```xml
<Provider Name="Windows Error Reporting"/>  <EventID>1001</EventID>
<Data>ServiceHang</Data>      <!-- third value: what Windows reported -->
<Data>ExampleSyncSvc</Data>   <!-- sixth value onward: the problem signature -->
<Data>examplesync.dll</Data>
```

**OCSF before → now:**

|                    | Before                                 | Now                                               |
| ------------------ | -------------------------------------- | ------------------------------------------------- |
| Class and activity | Process Activity · Terminate · Failure | Application Error · General Error                 |
| Severity           | Medium                                 | Informational                                     |
| Process            | Empty `process`, no `actor` (warnings) | Not set; the report stays in `unmapped.EventData` |

**Why:** 1001 says that Windows filed a problem report, and the third value says what for: `APPCRASH` for a crash, which Application Error 1000 already reports, and most often other problems, such as `ServiceHang` or Windows Update failures. No process terminated, so Process Activity doesn't fit.

#### Application hangs

**Windows writes** (Application Hang 1002):

```xml
<Provider Name="Application Hang"/>  <EventID>1002</EventID>
<Data Name="AppName">ExampleViewer.exe</Data>
<Data Name="ProcessId">0x23c8</Data>
<Data Name="HangType">Quiesce</Data>          <!-- kind of hang -->
```

**OCSF before → now:**

|                    | Before                                                | Now                               |
| ------------------ | ----------------------------------------------------- | --------------------------------- |
| Class and activity | Process Activity · Terminate · Failure                | Application Error · General Error |
| Hang type          | Not set                                               | `Quiesce`, in `status_detail`     |
| Process            | Empty `process` for named data, no `actor` (warnings) | Not set                           |

The report and the hung process stay in `unmapped.EventData`:

```tql
status_detail: "Quiesce",
unmapped: {EventData: {AppName: "ExampleViewer.exe", ProcessId: "0x23c8"}},
```

**Why:** 1002 says that an application stopped responding, but not who ended it. Process Activity requires an `actor`, but a hang event doesn't say whether the user or Windows closed the application.

*By @zedoraps.*

### No process objects without a process ID

Microsoft Defender, Windows Firewall, and AppX deployment events no longer build `actor.process`, and keep the raw value in `unmapped.EventData` instead.

#### Microsoft Defender

**Windows writes** (Microsoft Defender 1121, attack surface reduction block):

```xml
<Provider Name="Microsoft-Windows-Windows Defender"/>  <EventID>1121</EventID>
<Data Name="User">CORP\jdoe</Data>
<Data Name="Process Name">C:\Windows\System32\wbem\WmiPrvSE.exe</Data>  <!-- image path only -->
```

**OCSF before → now** (detections 1006, 1116, 1117 and attack surface reduction events 1121, 1122):

|                 | Before                                       | Now                                  |
| --------------- | -------------------------------------------- | ------------------------------------ |
| `actor.process` | From `Process Name`, without `pid` (warning) | Not set                              |
| Image path      | Not in `unmapped.EventData`                  | `unmapped.EventData["Process Name"]` |
| `actor.user`    | `{name: "jdoe", domain: "CORP"}`             | Unchanged                            |

**Why:** Defender names the process only by its image path and logs no process ID for it. An OCSF process needs a process ID, so the actor keeps only the user.

#### Windows Firewall

**Windows writes** (Windows Firewall 2004, rule added):

```xml
<Provider Name="Microsoft-Windows-Windows Firewall With Advanced Security"/>  <EventID>2004</EventID>
<Data Name="ModifyingUser">S-1-5-21-3471133136-2963561160-3931775028-1001</Data>
<Data Name="ModifyingApplication">C:\Windows\System32\netsh.exe</Data>  <!-- image path only -->
```

**OCSF before → now** (rule and configuration events 2003–2097):

|                 | Before                                               | Now                                       |
| --------------- | ---------------------------------------------------- | ----------------------------------------- |
| `actor.process` | From `ModifyingApplication`, without `pid` (warning) | Not set                                   |
| Image path      | Not in `unmapped.EventData`                          | `unmapped.EventData.ModifyingApplication` |
| `actor.user`    | From `ModifyingUser`                                 | Unchanged                                 |

**Why:** Windows Firewall names the program that changed the rule only by its image path, without a process ID, which an OCSF process needs.

#### AppX deployment

**Windows writes** (AppXDeployment-Server 400 and 404, three requesters):

```xml
<Data Name="CallingProcess">powershell.exe</Data>             <!-- a program -->
<Data Name="CallingProcess">svchost.exe,InstallService</Data> <!-- one service in svchost.exe -->
<Data Name="CallingProcess">svchost.exe,BITS,CryptSvc,DoSvc,EventSystem,InstallService,LicenseManager,Schedule,StorSvc,TokenBroker,UsoSvc,Winmgmt</Data>
```

**OCSF before → now:**

| `CallingProcess`             | Before                    | Now                                        |
| ---------------------------- | ------------------------- | ------------------------------------------ |
| `svchost.exe,InstallService` | `actor.process` (warning) | `actor.application.name: "InstallService"` |
| `powershell.exe`             | `actor.process` (warning) | `actor.application.name: "powershell.exe"` |
| Image with several services  | `actor.process` (warning) | No actor                                   |

AppX deployment events name the requester in `actor.application.name` and keep the raw value in `unmapped.EventData.CallingProcess`. Before, `unmapped.EventData` had neither `Process Name` nor `ModifyingApplication`.

**Why:** `CallingProcess` names the requester's image, followed by the services it hosts, but no process ID. A program or a single hosted service still names the requester as an application; an image that hosts several services doesn't say which one asked.

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

*By @zedoraps.*

### Same Windows event data from every collector

Security event data now carries the text of message-table tokens, and unnamed event data from legacy providers, such as Application Error, now uses the names `param1`, `param2`, … for all collectors, so Windows Event XML, Fluent Bit, and Winlogbeat produce the same event.

#### Message-table tokens

**Windows writes** (Security events in Windows Event XML):

```xml
<EventID>4826</EventID>  <Data Name="KernelDebug">%%1843</Data>          <!-- No -->
<EventID>4625</EventID>  <Data Name="FailureReason">%%2313</Data>       <!-- Unknown user name or bad password. -->
<EventID>4661</EventID>  <Data Name="AccessList">%%1537</Data>          <!-- DELETE -->
<EventID>4657</EventID>  <Data Name="NewValueType">%%1874</Data>        <!-- REG_EXPAND_SZ -->
<EventID>4719</EventID>  <Data Name="CategoryId">%%8272</Data>  <Data Name="AuditPolicyChanges">%%8448</Data>
```

Winlogbeat ships the text in the comments instead of the token.

**OCSF before → now:**

| Field                                   | Before                                       | Now                                                  |
| --------------------------------------- | -------------------------------------------- | ---------------------------------------------------- |
| `unmapped.EventData.KernelDebug` (4826) | `%%1843`                                     | `No`                                                 |
| `status_detail` (4625)                  | `%%2313`                                     | `Unknown user name or bad password.`                 |
| `access_list` (4661, 4662)              | `["%%1537"]`                                 | `["DELETE"]`                                         |
| `reg_value.type` (4657)                 | Not set                                      | `REG_EXPAND_SZ`                                      |
| 4719 `entity.policy.data`               | `category_id: "%%8272"`, `changes: "%%8448"` | `category: "System"`, `changes: ["Success removed"]` |
| Winlogbeat 4657 activity                | Unknown                                      | Set, Modify, or Delete                               |

Free-text fields, such as command lines, and unknown tokens stay unchanged.

**Why:** a `%%` token points into the provider's message table. Windows Event XML and Fluent Bit report the tokens, while Winlogbeat reports the text, so the same event looked different per collector, and the mapping couldn't read the registry value type or the Winlogbeat registry operation.

#### Unnamed event data

**Windows writes** (Application Error 1000 on Windows Server 2022):

```xml
<Provider Name="Application Error"/>  <EventID>1000</EventID>
<Data>ReportViewer.exe</Data>   <!-- %1 in the message -->
<Data>4.12.307.2</Data>         <!-- %2 -->
<Data>65a1b2c3</Data>           <!-- %3 -->
```

**OCSF before → now:**

| Collector                                                  | Before                           | Now                                               |
| ---------------------------------------------------------- | -------------------------------- | ------------------------------------------------- |
| Windows Event XML                                          | `unmapped.EventData._0`, `_1`, … | `param1`, `param2`, …                             |
| Winlogbeat                                                 | `param1`, `param2`, …            | Unchanged                                         |
| Windows Event XML, mixed with named data, such as `Binary` | Named fields broken              | Named fields keep their names, like in Winlogbeat |

**Why:** legacy providers write their values without names, and the mappings read them as `param1`, `param2`, …, the names that Winlogbeat uses and that match the `%1`, `%2` inserts of the provider's message. Windows Event XML parsing numbered them from `_0`, so these mappings found nothing.

**What you need to do**

| Query                                           | Effect | Replacement                                                                                          |
| ----------------------------------------------- | ------ | ---------------------------------------------------------------------------------------------------- |
| Tests on a token, such as `%%1843`              | Silent | Test the text, such as `No`                                                                          |
| Tests on 4719 `category_id` or `subcategory_id` | Silent | Test `category` or `subcategory`                                                                     |
| Tests on 4719 `changes` as a string             | Silent | `"Success removed" in entity.policy.data.changes`                                                    |
| Tests on `unmapped.EventData._0`                | Silent | Replace `unmapped.EventData._0` with `unmapped.EventData.param1`, and shift every other index by one |

*By @zedoraps.*

### Service and log service events in fitting classes

Service state reports from the Service Control Manager and Sysmon service state changes (4) now map to Application Lifecycle (6002), and Event Log service starts and stops now map to Event Log Activity.

#### Service Control Manager 7036, 7034, and 7023

**Windows writes** (Service Control Manager 7036):

```xml
<Provider Name="Service Control Manager"/>  <EventID>7036</EventID>
<Data Name="param1">ExampleUpdate</Data>    <!-- service display name -->
<Data Name="param2">running</Data>          <!-- new state -->
```

Crashes (7034) and terminations with an error (7023) look the same: `param1` names the service, and `param2` holds the crash count, such as `1`, or the error, such as `%%21`.

**OCSF before → now:**

|                                      | Before                                                                   | Now                                                             |
| ------------------------------------ | ------------------------------------------------------------------------ | --------------------------------------------------------------- |
| Class                                | Windows Service Activity                                                 | Application Lifecycle                                           |
| Activity, 7036 `running`             | Start                                                                    | Start · Success                                                 |
| Activity, 7036 `stopped`             | Stop                                                                     | Stop · Success                                                  |
| Activity, 7036 other states          | Pause for `paused`, else Other                                           | Other (`activity_name` = state)                                 |
| Activity, 7034 crashed               | Stop · Failure                                                           | Stop · Failure                                                  |
| Activity, 7023 terminated with error | Stop · Failure, error in `status_detail`                                 | Stop · Failure, error in `status_detail`                        |
| Service                              | `win_service: {name: "ExampleUpdate"}` (warning: no configuration field) | `application: {name: "ExampleUpdate", type: "Windows Service"}` |
| Actor                                | 7036 empty, 7034 and 7023 missing (warnings)                             | Not required; 7036 names the Service Control Manager process    |

**Why:** the events only say *which* service is now in *which* state, and how often it crashed or which error stopped it. They don't say who caused the change or how the service is configured. Windows Service Activity describes a process or user controlling a service and requires both; Application Lifecycle describes exactly "a service started or stopped".

#### Sysmon 4

**Windows writes** (Sysmon 4):

```xml
<Provider Name="Microsoft-Windows-Sysmon"/>  <EventID>4</EventID>
<Data Name="State">Started</Data>            <!-- new state of Sysmon -->
<Data Name="Version">15.14</Data>            <!-- Sysmon version -->
```

**OCSF before → now:**

|                        | Before                                                                              | Now                                                                        |
| ---------------------- | ----------------------------------------------------------------------------------- | -------------------------------------------------------------------------- |
| Class                  | Windows Service Activity                                                            | Application Lifecycle                                                      |
| Activity, `Started`    | Start                                                                               | Start                                                                      |
| Activity, `Stopped`    | Stop                                                                                | Stop                                                                       |
| Activity, other states | Stop                                                                                | Other                                                                      |
| Service                | `win_service: {name: "Sysmon", version: "15.14"}` (warning: no configuration field) | `application: {name: "Sysmon", type: "Windows Service", version: "15.14"}` |
| Actor                  | Empty (warning)                                                                     | Not set                                                                    |

**Why:** Sysmon reports only that it started or stopped, and its version. Like the Service Control Manager events, it doesn't say who changed the state or how the Sysmon service is configured, which Windows Service Activity requires.

#### Event Log 6005 and 6006

**Windows writes** (EventLog 6005; 6006 for the stop):

```xml
<Provider Name="EventLog"/>  <EventID>6005</EventID>
<Execution ProcessID="0" ThreadID="0"/>                            <!-- no process -->
<Binary>E8070B00000003000E000A000300F7020000000000000000</Binary>  <!-- start time -->
```

**OCSF before → now:**

|                | Before                                                                       | Now                        |
| -------------- | ---------------------------------------------------------------------------- | -------------------------- |
| Class          | Windows Service Activity                                                     | Event Log Activity         |
| Activity, 6005 | Start                                                                        | Start                      |
| Activity, 6006 | Stop                                                                         | Stop                       |
| Service        | `win_service: {name: "Windows Event Log"}` (warning: no configuration field) | `log_provider: "EventLog"` |
| Actor          | Missing (warning)                                                            | Not required               |

**Why:** the event says only that the event log service started or stopped; its data is the start time in binary form, without a process or account. Event Log Activity has Start and Stop activities for the logging service itself, while Windows Service Activity again needs an actor and a service configuration.

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

*By @zedoraps.*

## 🐞 Bug fixes

### Application crashes and Code Integrity

Application crashes (1000) now map the values that Windows writes, with or without field names, Code Integrity events now give the loading process its process and thread ID, and App Control audit and block events (3076/3077) now map the file, the loading process, and the signing levels.

#### Application crashes

**Windows writes** (Application Error 1000, Windows 10 and later):

```xml
<Provider Name="Application Error"/>  <EventID>1000</EventID>
<Data Name="ModuleName">ucrtbase.dll</Data>                 <!-- faulting module -->
<Data Name="ModulePath">C:\WINDOWS\System32\ucrtbase.dll</Data>
<Data Name="ProcessId">0x1f3c</Data>                        <!-- crashed process -->
<Data Name="ProcessCreationTime">0x1dbd3c7709c91e0</Data>
```

Windows Server 2022 writes the same values without names, and the process ID without `0x`, such as `1a2c`.

**OCSF before → now:**

|                                                   | Before               | Now                             |
| ------------------------------------------------- | -------------------- | ------------------------------- |
| `module.file`                                     | Positional data only | Also `ModuleName`, `ModulePath` |
| `module.load_type_id`                             | Not set (warning)    | `0` (Unknown)                   |
| `actor.process`                                   | Not set (warning)    | The crashed process             |
| `process.created_time`                            | Positional data only | Also `ProcessCreationTime`      |
| `process.pid` without hex letters, such as `2048` | Read as decimal      | Read as hexadecimal             |

**Why:** Windows writes the process ID in hexadecimal, even when it has no `0x` and no letters. The crash happened in the process's own code, so the crashed process is also the actor that Process Activity requires. The event doesn't say how the faulting module was loaded, and an OCSF module needs a load type or a function name.

#### Code Integrity

**Windows writes** (Code Integrity 3037):

```xml
<Provider Name="Microsoft-Windows-CodeIntegrity"/>  <EventID>3037</EventID>
<Execution ProcessID="3120" ThreadID="4056"/>       <!-- the loading process -->
<Data Name="FileNameBuffer">\Device\HarddiskVolume3\Users\jdoe\AppData\Local\Temp\unsigned.dll</Data>
<Data Name="ProcessNameBuffer">\Device\HarddiskVolume3\Windows\System32\rundll32.exe</Data>
```

**OCSF before → now:**

|                                             | Before            | Now                                             |
| ------------------------------------------- | ----------------- | ----------------------------------------------- |
| `actor.process.pid`, `ptid`                 | Not set (warning) | `3120`, `4056`, from the event header           |
| `actor.process` without a header process ID | Path only         | Not set; the name stays in `unmapped.EventData` |

**Why:** Code Integrity writes these events in the context of the loading process, so the header carries the ID of the process in `ProcessNameBuffer`. An OCSF process needs a `pid`, `uid`, or `cpid`, so without a header ID the process stays unmapped.

#### App Control audit and block events

**Windows writes** (Code Integrity 3076; 3077 for a block):

```xml
<EventID>3076</EventID>  <Execution ProcessID="7316" ThreadID="6020"/>
<Data Name="File Name">\Device\HarddiskVolume3\Users\lmorgan\AppData\Local\Temp\example-audit\plugin.dll</Data>
<Data Name="Process Name">\Device\HarddiskVolume3\Windows\System32\rundll32.exe</Data>
<Data Name="Requested Signing Level">2</Data>
<Data Name="Validated Signing Level">1</Data>
```

**OCSF before → now:**

|                                                                       | Before          | Now                                                                 |
| --------------------------------------------------------------------- | --------------- | ------------------------------------------------------------------- |
| `application.name`, `application.data.file_path`                      | Empty (warning) | `plugin.dll` and its path, from `File Name`                         |
| `actor.process`                                                       | Missing         | `rundll32.exe`, `pid: 7316`, from `Process Name` and the header     |
| `application.data.requested_signing_level`, `validated_signing_level` | Empty           | `2`, `1`, from `Requested Signing Level`, `Validated Signing Level` |

**Why:** App Control events name their fields with spaces, such as `File Name`, while other Code Integrity events use names such as `FileNameBuffer`, which were the only names that the mapping read.

Sigma rules that read `FileNameBuffer`, `ProcessNameBuffer`, or the signing levels now see these values.

*By @zedoraps.*

### Defender detection evidence

Microsoft Defender detections (1116/1117) now list each detected file on disk once in `evidences`, instead of one file holding the whole `Path` with its resource prefixes.

**Windows writes** (Microsoft Defender 1116):

```xml
<Provider Name="Microsoft-Windows-Windows Defender"/>  <EventID>1116</EventID>
<Data Name="Path">file:_C:\Users\rchen\Downloads\credtool.sys</Data>  <!-- resource type, then path -->
```

A detection with several resources lists them all in `Path`, separated by `; `, such as `containerfile:_C:\Users\rchen\Downloads\tools.zip; file:_C:\Users\rchen\Downloads\tools.zip->(Zip:credtool.exe); webfile:_C:\Users\rchen\Downloads\setup.exe|https://downloads.example.test/setup.exe|pid:4312,…`.

**OCSF before → now:**

| Resource in `Path`                               | Before                                                      | Now                        |
| ------------------------------------------------ | ----------------------------------------------------------- | -------------------------- |
| `file:_C:\x.exe`, `containerfile:_C:\x.zip`      | One file with the whole `Path` as its path, prefix included | The file                   |
| `file:_C:\x.zip->(Zip:y.exe)`                    | Part of that one file                                       | The container, `C:\x.zip`  |
| `webfile:_C:\x.exe`, followed by URL and process | Part of that one file                                       | The local path, `C:\x.exe` |
| `regkey:_…` and other resources                  | A file named after the last path element, such as `Run`     | None                       |

```tql
evidences: [
  {file: {path: "C:\\Users\\rchen\\Downloads\\tools.zip", name: "tools.zip", type_id: 1}},
  {file: {path: "C:\\Users\\rchen\\Downloads\\setup.exe", name: "setup.exe", type_id: 1}},
],
```

The complete list stays in `unmapped.EventData.Path`.

**Why:** Defender writes every detected resource into one `Path`, each with a type prefix, and only some of them are files on disk. A file evidence needs the path of such a file, so the mapping splits the list, strips the prefixes, and skips the other resources.

*By @zedoraps.*

### Microsoft Graph devices and risky users

Microsoft Graph sign-ins and Intune managed devices now set the operating system type from the reported platform, and Microsoft Entra ID risky users now identify their owner.

**Microsoft Graph writes:**

```json
// Sign-in: the device's platform, by name
{"deviceDetail": {"deviceId": "device-1", "operatingSystem": "Windows 11"}}
// Intune managed device
{"operatingSystem": "Windows", "osVersion": "11.0.26100"}
// Risky user: id is the ID of the user at risk
{"id": "user-1", "userDisplayName": "Alice Example"}
```

**OCSF before → now:**

| Source                                           | Field                                                                       | Before                                            | Now                                                                                |
| ------------------------------------------------ | --------------------------------------------------------------------------- | ------------------------------------------------- | ---------------------------------------------------------------------------------- |
| Sign-ins, managed devices                        | `src_endpoint.os.type_id` (sign-ins), `device.os.type_id` (managed devices) | Not set (warning)                                 | Such as `100` (Windows) for `Windows 11`                                           |
| Sign-ins, managed devices, unrecognized platform | Same                                                                        | Not set                                           | `99` (Other), name in `os.type`                                                    |
| Entra ID risky users                             | `resources[].owner.uid`                                                     | Not set; the owner had only `full_name` (warning) | The risky user's `id`, which Microsoft Graph defines as the ID of the user at risk |

**Why:** Microsoft Graph reports the platform only as a name, with varying case and often a version, while an OCSF operating system requires a type ID, so the mapping derives it from the start of the name. For risky users, the owner had only a display name, which doesn't identify an OCSF user, but the record's `id` does.

*By @zedoraps.*

### Services, AppX, PowerShell, and Sysmon

Service Control Manager events now have an actor when the event names one, failed AppX deployments report their error, PowerShell script block invocations name their host process, and Sysmon modules get a load type.

#### Service Control Manager actors

**Windows writes** (Service Control Manager 7036 and 7040):

```xml
<EventID>7036</EventID>  <Execution ProcessID="2844" ThreadID="6236"/>  <!-- Service Control Manager -->
<EventID>7040</EventID>  <Security UserID="S-1-5-18"/>                <!-- account in the header -->
```

**OCSF before → now:**

| Event                  | Before                  | Now                                      |
| ---------------------- | ----------------------- | ---------------------------------------- |
| 7036 state change      | Empty `actor` (warning) | `actor.process: {pid: 2844, ptid: 6236}` |
| 7040 start type change | Empty `actor` (warning) | `actor.user: {uid: "S-1-5-18"}`          |
| 7045 installation      | No `actor` (warning)    | `actor.user` from the header account     |

**Why:** the Service Control Manager performs a 7036 state change itself and writes its own process and thread ID into the header. For 7040 and 7045, the header's `UserID` names the account. The mapping left both in `unmapped.System`. Service Control Manager crashes (7034) and terminations with an error (7023) still have no actor, because the service stopped on its own.

#### AppX deployment failures

**Windows writes** (AppXDeployment-Server 404):

```xml
<EventID>404</EventID>
<Data Name="SummaryError">error 0x8000000B: Opening the package from location ddb8d18aad587a89160285fb6e0e8fc193dc04c2 failed.</Data>
<Data Name="PackageFullName"></Data>   <!-- no package -->
<Data Name="ErrorCode">0x80073cf0</Data>
```

**OCSF before → now:**

|                                             | Before                            | Now                                                                                  |
| ------------------------------------------- | --------------------------------- | ------------------------------------------------------------------------------------ |
| `status_detail`                             | Not set                           | `error 0x8000000B: Opening the package from location … failed.`, from `SummaryError` |
| `application`, deployment without a package | Built from empty fields (warning) | Not set (warning: Application Lifecycle requires an application)                     |

**Why:** a failed deployment explains the failure only in `SummaryError`, and when Windows couldn't open the package, `PackageFullName` is empty. An application with only empty fields identifies nothing, so the mapping leaves it out and accepts the warning that the class requires one.

#### PowerShell script block invocations

**Windows writes** (PowerShell 4105; 4106 for the stop):

```xml
<EventID>4105</EventID>
<Execution ProcessID="1804" ThreadID="2084"/>                          <!-- PowerShell host -->
<Data Name="ScriptBlockId">dc9383e3-693a-29e2-5e46-a40c8ca64948</Data>
<Data Name="RunspaceId">97c13651-7a4c-7bb2-4151-ab652c5a3cef</Data>
```

**OCSF before → now:**

| Event                                            | Before                                                 | Now                                                   |
| ------------------------------------------------ | ------------------------------------------------------ | ----------------------------------------------------- |
| 4105/4106 script block invocation start and stop | No `actor.process`; IDs in `unmapped.System.Execution` | PowerShell host's `pid` and `ptid`, `1804` and `2084` |

**Why:** the PowerShell host that runs the script block writes the event, so the header's process and thread ID are that host's, like in script block logging (4104), which the mapping already reads this way.

#### Sysmon modules

**Windows writes** (Sysmon 7 and 8):

```xml
<EventID>7</EventID>  <Data Name="ImageLoaded">C:\Users\jdoe\AppData\Local\Temp\evil.dll</Data>
<EventID>8</EventID>  <Data Name="StartAddress">0x00007FFAB1234560</Data>
                      <Data Name="StartFunction">-</Data>  <!-- no function -->
```

**OCSF before → now:**

| Event                                              | Before                             | Now           |
| -------------------------------------------------- | ---------------------------------- | ------------- |
| 7 image load                                       | No `module.load_type_id` (warning) | `0` (Unknown) |
| 8 remote thread creation, without a start function | No `module.load_type_id` (warning) | `0` (Unknown) |

**Why:** Sysmon names the loaded file or the thread's start address, but never says how the module was loaded, and remote threads often have no start function. OCSF requires a module to have a load type or a function name, so the load type is Unknown.

*By @zedoraps.*

### Windows Security event fields

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

| Event                        | Before                    | Now                                                                                                         |
| ---------------------------- | ------------------------- | ----------------------------------------------------------------------------------------------------------- |
| 4665/4667 client context     | No ID, no actor (warning) | Context ID in `entity.uid`, client in `actor.user`                                                          |
| 4870 revoked certificate     | No ID (warning)           | Serial number in `entity.uid`                                                                               |
| 4902 per-user audit policy   | No ID (warning)           | Policy ID in `entity.uid`                                                                                   |
| 4931–4933 replication        | No name (warning)         | Naming context in `entity.name`; 4932/4933 session in `entity.uid`; 4931/4933 `status_code` and `status_id` |
| 4673 privileged service call | No name (warning)         | Service, or else privileges, in `entity.name`                                                               |

**Why:** each of these events identifies its entity in a field of its own, which the mapping didn't read, so the entity had no name or ID, which OCSF requires. Most 4673 records write the service as `-`, so the exercised privileges name the call.

#### Subject process

**Windows writes** (Security 4674; 4661, 4670, and 4673 alike):

```xml
<EventID>4674</EventID>
<Data Name="ProcessId">0x12c</Data>                                 <!-- subject's process -->
<Data Name="ProcessName">C:\Windows\System32\notepad.exe</Data>
```

**OCSF before → now:**

| Event                  | Before                                             | Now                                                      |
| ---------------------- | -------------------------------------------------- | -------------------------------------------------------- |
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

| Event                             | Before                           | Now                                             |
| --------------------------------- | -------------------------------- | ----------------------------------------------- |
| 4826 Boot Configuration Data load | No name, ID, or device (warning) | Device that logged the event in `entity.device` |

**Why:** the event describes the loaded Boot Configuration Data only by its settings, with no name or ID. It belongs to the device that logs the event, so that device identifies the entity, which OCSF requires to have a name, ID, or device.

#### Access masks

**Windows writes** (Security 4674 and 4656):

```xml
<EventID>4674</EventID>  <Data Name="AccessMask">16777216</Data>  <!-- decimal, in some 4674 records -->
<EventID>4656</EventID>  <Data Name="AccessMask">0x12019f</Data>  <!-- hexadecimal -->
```

**OCSF before → now:**

| Event                                                                                                                            | Before                   | Now                     |
| -------------------------------------------------------------------------------------------------------------------------------- | ------------------------ | ----------------------- |
| Entity Management, decimal `AccessMask` `16777216` (some 4674 records), from collectors that ship it as text, such as Winlogbeat | `access_mask: 376926742` | `access_mask: 16777216` |
| Entity Management, decimal `AccessMask` `16777216`, Windows Event XML                                                            | `access_mask: 16777216`  | `access_mask: 16777216` |
| Entity Management, `AccessMask` `0x12019f`                                                                                       | Hexadecimal              | Hexadecimal             |

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

| Event                     | Before                                  | Now                                                |
| ------------------------- | --------------------------------------- | -------------------------------------------------- |
| Security 1102 log cleared | Empty user, session, process (warnings) | `actor.user`, `actor.session`, `actor.process.pid` |
| Eventlog 104 log cleared  | User only                               | `actor.user`, `actor.process.pid`                  |

```tql
actor: {
  user: {name: "lmorgan", domain: "EXAMPLE"},
  session: {uid_alt: "0x5d2e71"},
  process: {pid: 6212},
},
```

Sigma rules that read `SubjectUserName` or `SubjectUserSid` on 1102 now see a value.

**Why:** for cleared logs, the mapping read `EventData`, while Windows writes the data under `UserData/LogFileCleared`. Windows writes `ClientProcessId` in decimal, such as `6212`, which the 1102 mapping read as hexadecimal.

*By @zedoraps.*
