---
title: Defender events without a process object
type: change
authors:
  - zedoraps
created: 2026-11-19T00:55:28.245022Z
---

Microsoft Defender detections (1006, 1116, 1117) and attack surface reduction events (1121, 1122) no longer build `actor.process`; the actor keeps the user.

| Field | Before | Now |
|---|---|---|
| `actor.process` | From `Process Name`, without `pid` | Not set |
| `unmapped.EventData["Process Name"]` | Not set | The image path |

**What you need to do**

| Rule | Effect | Replacement |
|---|---|---|
| PSExec and WMI Process Creations Block | Silent | Match the unmapped field |

```tql
where class_uid == 2004 and metadata.event_code == "1121" and
  unmapped.EventData["Process Name"].to_lower().ends_with(r"\wmiprvse.exe")
```

**Why:** Defender logs no process ID, and an OCSF process needs one.
