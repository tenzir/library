---
title: Kill chain phases from STIX Indicators
type: feature
authors:
  - mavam
created: 2026-10-15T11:05:57.511896Z
---

`stix::ocsf::normalize` now maps the Lockheed Martin Cyber Kill Chain phases of STIX Indicators to `osint.kill_chain`. Each phase gets its OCSF phase ID, such as `3` for `delivery` or `6` for `command-and-control`. A phase outside the seven standard ones maps to `99` (Other) and keeps its STIX name. Phases of other kill chains remain under `unmapped`.
