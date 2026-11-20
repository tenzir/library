---
title: Device for loaded Boot Configuration Data
type: bugfix
authors:
  - zedoraps
created: 2026-11-19T01:06:11.094713Z
---

Boot Configuration Data load events (4826) now set `entity.device` to the device that logged the event.

**Why:** The entity had no name, ID, or device, which OCSF requires, because the event names the boot configuration only by its settings.
