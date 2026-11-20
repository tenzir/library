---
title: Defender events without a process object
type: change
authors:
  - zedoraps
created: 2026-11-19T00:55:28.245022Z
---

Microsoft Defender detections (1006, 1116, 1117) and attack surface reduction events (1121, 1122) no longer build `actor.process` from `Process Name`. The image path stays in `unmapped.EventData["Process Name"]`, and the actor keeps the user when Defender names one.

Defender names the process only by its image path and logs no process ID. An OCSF process needs a `pid`, `uid`, or `cpid`, so `ocsf_cast` warned about these events.

Tenzir's Sigma catalog reads `ProcessName` from `actor.process.path`, so Sigma rules that test it now see no value, and SigmaHQ's *PSExec and WMI Process Creations Block* no longer matches. Match the unmapped field instead:

```tql
where class_uid == 2004 and metadata.event_code == "1121" and
  unmapped.EventData["Process Name"].to_lower().ends_with(r"\wmiprvse.exe")
```
