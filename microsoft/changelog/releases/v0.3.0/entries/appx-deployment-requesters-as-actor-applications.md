---
title: AppX deployment requesters as actor applications
type: change
authors:
  - zedoraps
created: 2026-11-19T00:56:03.185003Z
---

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
