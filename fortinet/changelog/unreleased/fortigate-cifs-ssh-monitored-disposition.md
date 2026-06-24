---
title: FortiGate CIFS and SSH monitored disposition
type: change
authors:
  - jachris
prs:
  - 163
created: 2026-06-24T12:09:04.000000Z
---

FortiGate CIFS and SSH UTM logs with `action="monitored"` now map to OCSF
`disposition_id` 17 (Monitored) instead of 0 (Unknown), matching the other UTM
content-inspection mappers (webfilter, emailfilter, virus).
