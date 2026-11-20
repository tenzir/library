---
title: No process objects without a process ID
type: change
authors:
  - zedoraps
created: 2026-11-19T00:54:09.695523Z
---

Microsoft Defender, Windows Firewall, and AppX deployment events no longer build `actor.process`, and keep the raw value in `unmapped.EventData` instead.

#### Microsoft Defender

**Windows writes** (Microsoft Defender 1121, attack surface reduction block):

```xml
<Provider Name="Microsoft-Windows-Windows Defender"/>  <EventID>1121</EventID>
<Data Name="User">CORP\jdoe</Data>
<Data Name="Process Name">C:\Windows\System32\wbem\WmiPrvSE.exe</Data>  <!-- image path only -->
```

**OCSF before → now** (detections 1006, 1116, 1117 and attack surface reduction events 1121, 1122):

| | Before | Now |
|---|---|---|
| `actor.process` | From `Process Name`, without `pid` (warning) | Not set |
| Image path | Not in `unmapped.EventData` | `unmapped.EventData["Process Name"]` |
| `actor.user` | `{name: "jdoe", domain: "CORP"}` | Unchanged |

**Why:** Defender names the process only by its image path and logs no process ID for it. An OCSF process needs a process ID, so the actor keeps only the user.

#### Windows Firewall

**Windows writes** (Windows Firewall 2004, rule added):

```xml
<Provider Name="Microsoft-Windows-Windows Firewall With Advanced Security"/>  <EventID>2004</EventID>
<Data Name="ModifyingUser">S-1-5-21-3471133136-2963561160-3931775028-1001</Data>
<Data Name="ModifyingApplication">C:\Windows\System32\netsh.exe</Data>  <!-- image path only -->
```

**OCSF before → now** (rule and configuration events 2003–2097):

| | Before | Now |
|---|---|---|
| `actor.process` | From `ModifyingApplication`, without `pid` (warning) | Not set |
| Image path | Not in `unmapped.EventData` | `unmapped.EventData.ModifyingApplication` |
| `actor.user` | From `ModifyingUser` | Unchanged |

**Why:** Windows Firewall names the program that changed the rule only by its image path, without a process ID, which an OCSF process needs.

#### AppX deployment

**Windows writes** (AppXDeployment-Server 400 and 404, three requesters):

```xml
<Data Name="CallingProcess">powershell.exe</Data>             <!-- a program -->
<Data Name="CallingProcess">svchost.exe,InstallService</Data> <!-- one service in svchost.exe -->
<Data Name="CallingProcess">svchost.exe,BITS,CryptSvc,DoSvc,EventSystem,InstallService,LicenseManager,Schedule,StorSvc,TokenBroker,UsoSvc,Winmgmt</Data>
```

**OCSF before → now:**

| `CallingProcess` | Before | Now |
|---|---|---|
| `svchost.exe,InstallService` | `actor.process` (warning) | `actor.application.name: "InstallService"` |
| `powershell.exe` | `actor.process` (warning) | `actor.application.name: "powershell.exe"` |
| Image with several services | `actor.process` (warning) | No actor |

AppX deployment events name the requester in `actor.application.name` and keep the raw value in `unmapped.EventData.CallingProcess`. Before, `unmapped.EventData` had neither `Process Name` nor `ModifyingApplication`.

**Why:** `CallingProcess` names the requester's image, followed by the services it hosts, but no process ID. A program or a single hosted service still names the requester as an application; an image that hosts several services doesn't say which one asked.

**What you need to do**

| Rule | Source | Effect | Replacement |
|---|---|---|---|
| PSExec and WMI Process Creations Block | Defender | Silent | Match the unmapped field |
| New Firewall Rule Added In Windows Firewall Exception List Via WmiPrvSE.EXE | Windows Firewall | Silent | Match the unmapped field |
| A Rule Has Been Deleted From The Windows Firewall Exception List | Windows Firewall | Silent: its `ModifyingApplication: null` filter drops all events | Filter on the unmapped field |
| Exclusion-only rules, such as All Rules Have Been Deleted From The Windows Firewall Configuration | Windows Firewall | More alerts | Exclude on the unmapped field |
| Windows AppX Deployment Full Trust Package Installation | AppX deployment | More alerts: the `svchost.exe,AppReadiness` exclusion no longer applies | Exclude on the unmapped field |

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
