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

**What changes:**

- Detections (1116/1117) with Low (`1`) now get OCSF severity Low (`2`) instead of Informational (`1`).
- Detections (1116/1117) with Moderate (`2`) now get OCSF severity Medium (`3`) instead of Low (`2`).
- Unknown (`0`), High (`4`), and Severe (`5`) map as before.
- Undocumented severities now map to Other (`99`), keeping the name or ID in `severity`, for all Defender events. Detections previously copied the ID; threat and quarantine events used Unknown (`0`).
- Detections without a severity now get Unknown (`0`).
