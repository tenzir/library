---
title: Service Control Manager state reports as Application Lifecycle events
type: change
authors:
  - zedoraps
created: 2026-11-19T13:03:46.875364Z
---

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
