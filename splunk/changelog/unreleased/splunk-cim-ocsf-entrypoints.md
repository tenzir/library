---
title: Splunk CIM and OCSF mapping entry points
type: feature
authors:
  - mavam
  - codex
prs:
  - 154
created: 2026-06-08T00:00:00Z
---

The Splunk package now exposes `splunk::cim::map` as the canonical entry point
for mapping supported events to Splunk CIM and `splunk::ocsf::map` as the
canonical entry point for mapping supported events to OCSF. The OCSF-specific
CIM mapper moved to `splunk::cim::ocsf::map`, and the previous
`splunk::cim::from_ocsf` namespace was removed before release.

The CIM-to-OCSF mapper covers Splunk CIM DNS, Endpoint, Change, Alerts,
Vulnerabilities, Authentication, Network Traffic, Email, Network Sessions VPN,
Data Access, Database Query, and Web events and emits the corresponding OCSF
1.8 event classes.
