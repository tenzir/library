---
title: Service and log service events in fitting classes
type: change
authors:
  - zedoraps
created: 2026-11-18T10:40:09.280288Z
---

Service state reports from the Service Control Manager and Sysmon service state changes (4) now map to Application Lifecycle (6002), and Event Log service starts and stops now map to Event Log Activity.

| Event | Before | Now |
|---|---|---|
| Service Control Manager 7036 `running` | Windows Service Activity | Application Lifecycle · Start · Success |
| Service Control Manager 7036 `stopped` | Windows Service Activity | Application Lifecycle · Stop · Success |
| Service Control Manager 7036 other states | Windows Service Activity | Application Lifecycle · Other (`activity_name` = state) |
| Service Control Manager 7034 crashed | Windows Service Activity | Application Lifecycle · Stop · Failure |
| Service Control Manager 7023 terminated with error | Windows Service Activity | Application Lifecycle · Stop · Failure, error in `status_detail` |
| Sysmon 4 `Started` | Windows Service Activity · Start | Application Lifecycle · Start |
| Sysmon 4 `Stopped` | Windows Service Activity · Stop | Application Lifecycle · Stop |
| Sysmon 4 other states | Windows Service Activity · Stop | Application Lifecycle · Other |
| Event Log 6005 | Windows Service Activity · Start | Event Log Activity · Start |
| Event Log 6006 | Windows Service Activity · Stop | Event Log Activity · Stop |

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

**Why:** The Service Control Manager and Sysmon events name neither the service configuration nor an actor, both of which Windows Service Activity requires.
