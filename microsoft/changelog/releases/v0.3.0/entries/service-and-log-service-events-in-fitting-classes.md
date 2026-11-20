---
title: Service and log service events in fitting classes
type: change
authors:
  - zedoraps
created: 2026-11-18T10:40:09.280288Z
---

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

| | Before | Now |
|---|---|---|
| Class | Windows Service Activity | Application Lifecycle |
| Activity, 7036 `running` | Start | Start · Success |
| Activity, 7036 `stopped` | Stop | Stop · Success |
| Activity, 7036 other states | Pause for `paused`, else Other | Other (`activity_name` = state) |
| Activity, 7034 crashed | Stop · Failure | Stop · Failure |
| Activity, 7023 terminated with error | Stop · Failure, error in `status_detail` | Stop · Failure, error in `status_detail` |
| Service | `win_service: {name: "ExampleUpdate"}` (warning: no configuration field) | `application: {name: "ExampleUpdate", type: "Windows Service"}` |
| Actor | 7036 empty, 7034 and 7023 missing (warnings) | Not required; 7036 names the Service Control Manager process |

**Why:** the events only say *which* service is now in *which* state, and how often it crashed or which error stopped it. They don't say who caused the change or how the service is configured. Windows Service Activity describes a process or user controlling a service and requires both; Application Lifecycle describes exactly "a service started or stopped".

#### Sysmon 4

**Windows writes** (Sysmon 4):

```xml
<Provider Name="Microsoft-Windows-Sysmon"/>  <EventID>4</EventID>
<Data Name="State">Started</Data>            <!-- new state of Sysmon -->
<Data Name="Version">15.14</Data>            <!-- Sysmon version -->
```

**OCSF before → now:**

| | Before | Now |
|---|---|---|
| Class | Windows Service Activity | Application Lifecycle |
| Activity, `Started` | Start | Start |
| Activity, `Stopped` | Stop | Stop |
| Activity, other states | Stop | Other |
| Service | `win_service: {name: "Sysmon", version: "15.14"}` (warning: no configuration field) | `application: {name: "Sysmon", type: "Windows Service", version: "15.14"}` |
| Actor | Empty (warning) | Not set |

**Why:** Sysmon reports only that it started or stopped, and its version. Like the Service Control Manager events, it doesn't say who changed the state or how the Sysmon service is configured, which Windows Service Activity requires.

#### Event Log 6005 and 6006

**Windows writes** (EventLog 6005; 6006 for the stop):

```xml
<Provider Name="EventLog"/>  <EventID>6005</EventID>
<Execution ProcessID="0" ThreadID="0"/>                            <!-- no process -->
<Binary>E8070B00000003000E000A000300F7020000000000000000</Binary>  <!-- start time -->
```

**OCSF before → now:**

| | Before | Now |
|---|---|---|
| Class | Windows Service Activity | Event Log Activity |
| Activity, 6005 | Start | Start |
| Activity, 6006 | Stop | Stop |
| Service | `win_service: {name: "Windows Event Log"}` (warning: no configuration field) | `log_provider: "EventLog"` |
| Actor | Missing (warning) | Not required |

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

| Rule | Effect | Replacement |
|---|---|---|
| Windows Defender Threat Detection Service Disabled | Silent | 7036, Defender stopped |
| Important Windows Service Terminated Unexpectedly | Silent | 7034, service name |
| Important Windows Service Terminated With Error | Silent | 7023, service name |
| Windows Service Terminated With Error | Silent | 7023 |

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
