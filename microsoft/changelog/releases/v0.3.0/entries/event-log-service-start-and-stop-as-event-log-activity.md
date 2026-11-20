---
title: Event Log service start and stop as Event Log Activity
type: change
authors:
  - zedoraps
created: 2026-11-18T10:40:09.280288Z
---

Event Log service starts (6005) and stops (6006) now map to Event Log Activity with the Start and Stop activities instead of Windows Service Activity. Like the other Event Log service events, they name the logging service in `log_provider`.
