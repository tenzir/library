---
title: Application crashes and Code Integrity
type: bugfix
authors:
  - zedoraps
created: 2026-11-18T10:40:09.905177Z
---

Application crashes (1000) now map the values that Windows writes, with or without field names, Code Integrity events now give the loading process its process and thread ID, and App Control audit and block events (3076/3077) now map the file, the loading process, and the signing levels.

#### Application crashes

**Windows writes** (Application Error 1000, Windows 10 and later):

```xml
<Provider Name="Application Error"/>  <EventID>1000</EventID>
<Data Name="ModuleName">ucrtbase.dll</Data>                 <!-- faulting module -->
<Data Name="ModulePath">C:\WINDOWS\System32\ucrtbase.dll</Data>
<Data Name="ProcessId">0x1f3c</Data>                        <!-- crashed process -->
<Data Name="ProcessCreationTime">0x1dbd3c7709c91e0</Data>
```

Windows Server 2022 writes the same values without names, and the process ID without `0x`, such as `1a2c`.

**OCSF before → now:**

| | Before | Now |
|---|---|---|
| `module.file` | Positional data only | Also `ModuleName`, `ModulePath` |
| `module.load_type_id` | Not set (warning) | `0` (Unknown) |
| `actor.process` | Not set (warning) | The crashed process |
| `process.created_time` | Positional data only | Also `ProcessCreationTime` |
| `process.pid` without hex letters, such as `2048` | Read as decimal | Read as hexadecimal |

**Why:** Windows writes the process ID in hexadecimal, even when it has no `0x` and no letters. The crash happened in the process's own code, so the crashed process is also the actor that Process Activity requires. The event doesn't say how the faulting module was loaded, and an OCSF module needs a load type or a function name.

#### Code Integrity

**Windows writes** (Code Integrity 3037):

```xml
<Provider Name="Microsoft-Windows-CodeIntegrity"/>  <EventID>3037</EventID>
<Execution ProcessID="3120" ThreadID="4056"/>       <!-- the loading process -->
<Data Name="FileNameBuffer">\Device\HarddiskVolume3\Users\jdoe\AppData\Local\Temp\unsigned.dll</Data>
<Data Name="ProcessNameBuffer">\Device\HarddiskVolume3\Windows\System32\rundll32.exe</Data>
```

**OCSF before → now:**

| | Before | Now |
|---|---|---|
| `actor.process.pid`, `ptid` | Not set (warning) | `3120`, `4056`, from the event header |
| `actor.process` without a header process ID | Path only | Not set; the name stays in `unmapped.EventData` |

**Why:** Code Integrity writes these events in the context of the loading process, so the header carries the ID of the process in `ProcessNameBuffer`. An OCSF process needs a `pid`, `uid`, or `cpid`, so without a header ID the process stays unmapped.

#### App Control audit and block events

**Windows writes** (Code Integrity 3076; 3077 for a block):

```xml
<EventID>3076</EventID>  <Execution ProcessID="7316" ThreadID="6020"/>
<Data Name="File Name">\Device\HarddiskVolume3\Users\lmorgan\AppData\Local\Temp\example-audit\plugin.dll</Data>
<Data Name="Process Name">\Device\HarddiskVolume3\Windows\System32\rundll32.exe</Data>
<Data Name="Requested Signing Level">2</Data>
<Data Name="Validated Signing Level">1</Data>
```

**OCSF before → now:**

| | Before | Now |
|---|---|---|
| `application.name`, `application.data.file_path` | Empty (warning) | `plugin.dll` and its path, from `File Name` |
| `actor.process` | Missing | `rundll32.exe`, `pid: 7316`, from `Process Name` and the header |
| `application.data.requested_signing_level`, `validated_signing_level` | Empty | `2`, `1`, from `Requested Signing Level`, `Validated Signing Level` |

**Why:** App Control events name their fields with spaces, such as `File Name`, while other Code Integrity events use names such as `FileNameBuffer`, which were the only names that the mapping read.

Sigma rules that read `FileNameBuffer`, `ProcessNameBuffer`, or the signing levels now see these values.
