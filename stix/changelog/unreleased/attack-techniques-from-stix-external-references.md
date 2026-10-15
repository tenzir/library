---
title: ATT&CK techniques from STIX external references
type: feature
authors:
  - mavam
created: 2026-10-15T10:24:13.473711Z
---

`stix::ocsf::normalize` now maps the MITRE ATT&CK external references of STIX Indicators to `osint.attacks`. A reference with the source name `mitre-attack` and an `external_id` such as `TA0002`, `T1059`, or `T1059.001` becomes a structured ATT&CK tactic, technique, or sub-technique that links to its ATT&CK page. Previously, these references only appeared as URLs in `osint.references`.
