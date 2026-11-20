---
title: Device for loaded Boot Configuration Data
type: bugfix
authors:
  - zedoraps
created: 2026-11-19T01:06:11.094713Z
---

Boot Configuration Data load events (4826) now identify the managed entity by the device that logged the event, in `entity.device`.

The event names the boot configuration only by its settings, so the entity had no name, ID, or device, which OCSF requires, and `ocsf_cast` warned about every such event.
