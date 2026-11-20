---
title: Services, AppX, PowerShell, and Sysmon
type: bugfix
authors:
  - zedoraps
created: 2026-11-18T10:40:10.548534Z
---

Service Control Manager events now have an actor when the event names one, failed AppX deployments report their error, PowerShell script block invocations name their host process, and Sysmon modules get a load type.

| Event | Field | Before | Now |
|---|---|---|---|
| Service Control Manager 7036 state change | `actor.process` | No actor | Service Control Manager `pid` and `ptid` |
| Service Control Manager 7040 start type change, 7045 installation | `actor.user` | No actor | Header account |
| AppX deployment 404 failure | `status_detail` | Not set | Error text from `SummaryError` |
| AppX deployment without a package | `application` | Built from empty fields | Not set |
| PowerShell 4105/4106 script block invocation start and stop | `actor.process` | Not set | PowerShell host's `pid` and `ptid`, like script block logging (4104) |
| Sysmon 7 image load, 8 remote thread creation, without a start function | `module.load_type_id` | Not set | `0` (Unknown) |

Service Control Manager crashes (7034) and terminations with an error (7023) still have no actor, because the service stopped on its own.

**Why:** OCSF requires a module to have a load type or a function name, and Sysmon doesn't report how a module was loaded.
