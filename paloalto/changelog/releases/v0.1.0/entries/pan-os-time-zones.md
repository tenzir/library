---
title: Time zone of PAN-OS times
type: feature
authors:
  - zedoraps
created: 2026-11-20T19:30:00Z
---

PAN-OS times without a zone are now interpreted in the zone of the new optional `timezone` argument of `paloalto::parse` and `paloalto::ocsf::normalize`, such as `timezone="Europe/Berlin"`, else in the offset of the record's high-resolution timestamp, and only then in UTC.
