---
title: No process objects without a process ID
type: change
authors:
  - zedoraps
created: 2026-11-19T00:54:09.695523Z
---

Microsoft Defender, Windows Firewall, and AppX deployment events no longer build `actor.process`, and keep the raw value in `unmapped.EventData` instead.

| Source | Before | Now |
|---|---|---|
| Defender detections (1006, 1116, 1117) and attack surface reduction events (1121, 1122) | `actor.process` from `Process Name`, without `pid` | Image path in `unmapped.EventData["Process Name"]`; the actor keeps the user |
| Windows Firewall rule and configuration events (2003–2097) | `actor.process` from `ModifyingApplication`, without `pid` | Image path in `unmapped.EventData.ModifyingApplication`; the actor keeps the user from `ModifyingUser` |
| AppX deployment, `CallingProcess` `svchost.exe,InstallService` | `actor.process` | `actor.application.name: "InstallService"` |
| AppX deployment, `CallingProcess` `powershell.exe` | `actor.process` | `actor.application.name: "powershell.exe"` |
| AppX deployment, image with several services | `actor.process` | No actor |

AppX deployment events name the requester in `actor.application.name` and keep the raw value in `unmapped.EventData.CallingProcess`. Before, `unmapped.EventData` had neither `Process Name` nor `ModifyingApplication`.

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

**Why:** Defender and Windows Firewall log no process ID, nor does Windows for the AppX requester, and an OCSF process needs one.
