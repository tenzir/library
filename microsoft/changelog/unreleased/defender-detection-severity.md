---
title: Defender detection severity
type: bugfix
authors:
  - zedoraps
created: 2026-11-20T17:24:41.718585Z
---

Microsoft Defender detections (1116/1117) now translate the Defender threat severity to the OCSF `severity_id` with the same table as threat (1006/1007) and quarantine (1009/1011) events, and all of them map an undocumented severity to Other.

**Windows writes** (Microsoft Defender 1116):

```xml
<Provider Name="Microsoft-Windows-Windows Defender"/>  <EventID>1116</EventID>
<Data Name="Severity ID">2</Data>          <!-- Defender scale: 1 Low, 2 Moderate, 4 High, 5 Severe -->
<Data Name="Severity Name">Moderate</Data>
```

Threat events (1006/1007) write only the name, such as `<Data Name="Severity">Moderate</Data>`.

**OCSF before → now:**

| Defender severity | Event | Before | Now |
|---|---|---|---|
| `1` Low | 1116/1117 | `1` (Informational) | `2` (Low) |
| `2` Moderate | 1116/1117 | `2` (Low) | `3` (Medium) |
| `0` Unknown, `4` High, `5` Severe | all | Unchanged | Unchanged |
| An undocumented ID, such as `3` | 1116/1117 | The ID, such as `3` (Medium) | `99` (Other), with the name or the ID as `severity` |
| An undocumented ID or name | 1006/1007, 1009/1011 | `0` (Unknown) | `99` (Other), with the name or the ID as `severity` |
| None | 1116/1117 | Not set | `0` (Unknown) |

**Why:** Defender numbers its threat severities 1 Low, 2 Moderate, 4 High, and 5 Severe, while OCSF numbers 1 Informational, 2 Low, 3 Medium, 4 High, and 5 Critical, so the detection mapping copied the number and lowered Low and Moderate threats by one level. All Defender events now share one table in the package constants.

No Sigma rule in the package filters on severity.
