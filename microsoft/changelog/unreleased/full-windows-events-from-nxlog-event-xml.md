---
title: Full Windows events from NXLog event XML
type: change
authors:
  - zedoraps
created: 2026-11-20T17:43:55.027261Z
---

Windows events from NXLog Enterprise Edition with `CaptureEventXML TRUE` now normalize from the event XML, so they map to the same OCSF events as natively collected ones.

**NXLog writes** (Enterprise Edition, `CaptureEventXML TRUE`, `to_json()`):

```json
{"EventID": 104, "SourceName": "Microsoft-Windows-Eventlog", "Message": "The Example/Operational log file was cleared.",
 "EventXML": "<Event xmlns='http://schemas.microsoft.com/win/2004/08/events/event'><System>…</System><UserData><LogFileCleared …><ClientProcessId>7716</ClientProcessId>…</LogFileCleared></UserData></Event>"}
```

**OCSF before → now:**

| Field | Before | Now |
|---|---|---|
| Unnamed event data, `UserData` (such as `actor.process.pid` of Eventlog 104) | Not set | From the XML |
| `unmapped.EventData` | NXLog's flat copies of the event data | The event data of the XML |
| `unmapped.NXLog.event_xml` | The XML | Not set |
| `message`, `metadata.loggers`, `unmapped.NXLog` | NXLog's message and metadata | Unchanged |

**What you need to do**

With NXLog Enterprise Edition, add `CaptureEventXML TRUE` to the `im_msvistalog` input. NXLog Community Edition rejects this option and drops unnamed event data, binary data, and `UserData` for good.

**Why:** NXLog's own fields lose values that the event XML keeps. Reading the XML gives every NXLog Enterprise Edition user the full event without extra configuration in the pipeline.
