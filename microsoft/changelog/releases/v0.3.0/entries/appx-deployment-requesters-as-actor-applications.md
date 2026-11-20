---
title: AppX deployment requesters as actor applications
type: change
authors:
  - zedoraps
created: 2026-11-19T00:56:03.185003Z
---

AppX deployment events now name the requester in `actor.application.name` instead of `actor.process`, and keep the raw value in `unmapped.EventData.CallingProcess`.

| `CallingProcess` | Before | Now |
|---|---|---|
| `svchost.exe,InstallService` | `actor.process` | `actor.application.name: "InstallService"` |
| `powershell.exe` | `actor.process` | `actor.application.name: "powershell.exe"` |
| Image with several services | `actor.process` | No actor |

**What you need to do**

| Rule | Effect | Replacement |
|---|---|---|
| Windows AppX Deployment Full Trust Package Installation | More alerts: the `svchost.exe,AppReadiness` exclusion no longer applies | Exclude on the unmapped field |

```tql
where class_uid == 6002 and metadata.event_code == "400" and
  application.data.has_full_trust == true and
  not unmapped.EventData.CallingProcess.starts_with("svchost.exe,AppReadiness")
```

**Why:** Windows logs no process ID for the requester, and an OCSF process needs one.
