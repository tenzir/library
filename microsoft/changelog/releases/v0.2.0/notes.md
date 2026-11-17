This release corrects how the Microsoft package maps Windows Security, Task Scheduler, Defender, PowerShell, WMI, and Sysmon events to OCSF 1.9.0.

## 🔧 Changes

### PowerShell engine errors as Application Error events

PowerShell engine errors (4100) are now Application Error events instead of Script Activity, because they report an error message rather than a script. The error lands in `message`, and the event reports the host command line and the user instead of treating the context block as the script.

*By @zedoraps in #209.*

### Task Scheduler actors and launch activities

Task Scheduler events take the actor from the user context, from the user that changed a registration (140–142), or from the scheduler account. The PIDs of launched task processes stay in `unmapped` instead of appearing as the actor.

Launch requests by users (110) and queued launches (325) are now Scheduled Job Activity events, and Other activities name the source activity.

*By @zedoraps in #209.*

### WMI subscriptions as Entity Management events

WMI permanent subscription bindings (5861) and Sysmon WMI events (19–21) are now Entity Management events. Both name a binding by its filter and consumer.

*By @zedoraps in #209.*

## 🐞 Bug fixes

### Accurate details of Windows security events

- Process creation (4688) names the creator as `actor.process`.
- System access changes (4717, 4718) list the granted or removed rights in `privileges`.
- Account lockouts (4740) report the caller computer in `src_endpoint` instead of `user.domain`.
- NTLM validation (4776) names the validating domain controller and the package of unknown protocols.
- Share access (5140) no longer reports a file without a name, and Remote Desktop sessions are inbound connections.
- Security package events (4610, 4611, 4614, 4622) identify the LSA process by its PID and the account that registered a trusted logon process, and report an unknown load type for the package.
- Registry value changes (4657) no longer report Windows message tokens as value types.
- Account lifecycle events keep real display names and principal names, while Windows message tokens stay in `unmapped`.

*By @zedoraps in #209.*

### Accurate Windows logon and logoff events

Logons report the System logon type of Windows (`0`) as OCSF `1`, logoffs report the logon type of the ended session, and failed logons report the failure reason in `status_detail`. Logon process names lose the padding that Windows adds.

Logons without an address or workstation, logoffs, and explicit credential logons from local callers no longer carry empty endpoints or actors. The all-zero logon GUID no longer becomes a session ID that links unrelated sessions.

*By @zedoraps in #209.*

### Defender attack surface reduction events and detections

Attack surface reduction events (1121 block, 1122 audit) read the fields that Defender actually writes. They report the rule as the analytic with its name, and the acting process, the user, and the targeted file. Defender detections classify the malware by its category, and an absent action no longer becomes an Other disposition.

*By @zedoraps in #209.*

### Required OCSF attributes for all Windows events

Every Windows event declares the version and ID of the `win` extension, and an unknown device type for the device and the collector, which OCSF requires.

*By @zedoraps in #209.*

### Sysmon accounts, pipes, and remote thread modules

Sysmon events report an unresolved account SID in `user.uid` instead of `user.name` and treat `-` as absent. Pipe events name pipes as named pipes, process tampering (25) carries its tampering type, and remote threads (8) describe their start module as a file with its path.

*By @zedoraps in #209.*
