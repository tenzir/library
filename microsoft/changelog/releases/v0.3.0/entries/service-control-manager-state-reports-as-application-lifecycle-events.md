---
title: Service Control Manager state reports as Application Lifecycle events
type: change
authors:
  - zedoraps
created: 2026-11-19T13:03:46.875364Z
---

Service state reports from the Service Control Manager are now Application Lifecycle (6002) events with the service as `application`.

| Event | Before | Now |
|---|---|---|
| 7036 `running` | Windows Service Activity | Application Lifecycle · Start · Success |
| 7036 `stopped` | Windows Service Activity | Application Lifecycle · Stop · Success |
| 7036 other states | Windows Service Activity | Application Lifecycle · Other (`activity_name` = state) |
| 7034 crashed | Windows Service Activity | Application Lifecycle · Stop · Failure |
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

**Why:** The events name neither the service configuration nor an actor, both of which Windows Service Activity requires.
