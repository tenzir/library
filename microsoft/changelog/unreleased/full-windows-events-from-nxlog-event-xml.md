---
title: Full Windows events from NXLog event XML
type: change
authors:
  - zedoraps
created: 2026-11-20T17:43:55.027261Z
---

Windows events from NXLog Enterprise Edition with `CaptureEventXML TRUE` now normalize from the event XML and map to the same OCSF events as natively collected ones.

- Unnamed event data and `UserData`, such as the client process of a cleared log (104), are now mapped.
- `unmapped.EventData` holds the event data of the XML instead of NXLog's flat copies.
- NXLog's message and metadata stay in `message`, `metadata.loggers`, and `unmapped.NXLog`.
