---
title: Event Log service start and stop as Event Log Activity
type: change
authors:
  - zedoraps
created: 2026-11-18T10:40:09.280288Z
---

Event Log service starts and stops now map to Event Log Activity, with the logging service in `log_provider`.

| Event | Before | Now |
|---|---|---|
| 6005 | Windows Service Activity · Start | Event Log Activity · Start |
| 6006 | Windows Service Activity · Stop | Event Log Activity · Stop |
