---
title: Accurate OCSF semantics for Windows events
type: bugfix
authors:
  - zedoraps
prs:
  - 209
created: 2026-08-29T10:25:02.375909Z
---

Several Windows mappings put source fields into OCSF attributes with a different meaning, missed fields that real events carry, or produced objects that OCSF considers invalid. They now map as follows:

- Every event declares the version and ID of the `win` extension and an unknown device type for the device and the collector, which OCSF requires.
- Logons report the System logon type of Windows (`0`) as OCSF `1`, logoffs report the logon type of the ended session, failed logons report the failure reason in `status_detail`, and logon process names lose the padding that Windows adds. Logons without an address or workstation, logoffs, and explicit credential logons from local callers no longer carry empty endpoints or actors, and the all-zero logon GUID no longer becomes a session ID that links unrelated sessions.
- Process creation (4688) names the creator as `actor.process`. System access changes (4717, 4718) list the granted or removed rights in `privileges`. Account lockouts (4740) report the caller computer in `src_endpoint` instead of `user.domain`. NTLM validation (4776) names the validating domain controller and the package of unknown protocols. Share access (5140) no longer reports a file without a name, and Remote Desktop sessions are inbound connections.
- Security package events (4610, 4611, 4614, 4622) identify the LSA process by its PID and the account that registered a trusted logon process.
- Task Scheduler events take the actor from the user context, from the user that changed a registration (140–142), or from the scheduler account, and keep the PIDs of launched task processes in `unmapped` instead of reporting them as the actor. Launch requests by users (110) and queued launches (325) are now Scheduled Job Activity, and Other activities name the source activity.
- Defender attack surface reduction events (1121 block, 1122 audit) read the fields that Defender writes, report the rule as the analytic with its name, the acting process, the user, and the targeted file. Defender detections classify the malware by its category, and an absent action no longer becomes an Other disposition.
- PowerShell engine errors (4100) report the error message, the host command line, and the user, instead of treating the context block as the script.
- WMI permanent subscription bindings (5861) and Sysmon WMI events (19–21) are now Entity Management events. Both name a binding by its filter and consumer.
- Sysmon events report an unresolved account SID in `user.uid` instead of `user.name`, treat `-` as absent, name pipes as named pipes, carry the tampering type of process tampering (25), and describe the start module of remote threads (8) as a file with its path.
- Security registry value changes (4657) no longer report Windows message tokens as value types.
- Account lifecycle events keep real display names and principal names, while Windows message tokens stay in `unmapped`.

Validation continues to report the process objects that Windows describes without a PID, such as logon processes and processes in Defender, firewall, and code integrity events, the load type of LSA packages, and the scripts of PowerShell events that carry no script text.
