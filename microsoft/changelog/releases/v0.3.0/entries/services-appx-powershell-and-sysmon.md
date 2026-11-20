---
title: Services, AppX, PowerShell, and Sysmon
type: bugfix
authors:
  - zedoraps
created: 2026-11-18T10:40:10.548534Z
---

Service Control Manager events now have an actor when the event names one, failed AppX deployments report their error, PowerShell script block invocations name their host process, and Sysmon modules get a load type.

#### Service Control Manager actors

**Windows writes** (Service Control Manager 7036 and 7040):

```xml
<EventID>7036</EventID>  <Execution ProcessID="2844" ThreadID="6236"/>  <!-- Service Control Manager -->
<EventID>7040</EventID>  <Security UserID="S-1-5-18"/>                <!-- account in the header -->
```

**OCSF before → now:**

| Event | Before | Now |
|---|---|---|
| 7036 state change | Empty `actor` (warning) | `actor.process: {pid: 2844, ptid: 6236}` |
| 7040 start type change | Empty `actor` (warning) | `actor.user: {uid: "S-1-5-18"}` |
| 7045 installation | No `actor` (warning) | `actor.user` from the header account |

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

| | Before | Now |
|---|---|---|
| `status_detail` | Not set | `error 0x8000000B: Opening the package from location … failed.`, from `SummaryError` |
| `application`, deployment without a package | Built from empty fields (warning) | Not set |

**Why:** a failed deployment explains the failure only in `SummaryError`, and when Windows couldn't open the package, `PackageFullName` is empty. An application with only empty fields identifies nothing, so the mapping leaves it out.

#### PowerShell script block invocations

**Windows writes** (PowerShell 4105; 4106 for the stop):

```xml
<EventID>4105</EventID>
<Execution ProcessID="1804" ThreadID="2084"/>                          <!-- PowerShell host -->
<Data Name="ScriptBlockId">dc9383e3-693a-29e2-5e46-a40c8ca64948</Data>
<Data Name="RunspaceId">97c13651-7a4c-7bb2-4151-ab652c5a3cef</Data>
```

**OCSF before → now:**

| Event | Before | Now |
|---|---|---|
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

| Event | Before | Now |
|---|---|---|
| 7 image load | No `module.load_type_id` (warning) | `0` (Unknown) |
| 8 remote thread creation, without a start function | No `module.load_type_id` (warning) | `0` (Unknown) |

**Why:** Sysmon names the loaded file or the thread's start address, but never says how the module was loaded, and remote threads often have no start function. OCSF requires a module to have a load type or a function name, so the load type is Unknown.
