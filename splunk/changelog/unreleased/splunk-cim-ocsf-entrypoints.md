---
title: Splunk CIM and OCSF mapping entry points
type: feature
authors:
  - mavam
  - codex
created: 2026-06-08T00:00:00Z
---

The Splunk package now exposes `splunk::cim::map` as the canonical entry point
for mapping supported events to Splunk CIM and `splunk::ocsf::map` as the
canonical entry point for mapping supported events to OCSF. The OCSF-specific
CIM mapper moved to `splunk::cim::ocsf::map`, and the previous
`splunk::cim::from_ocsf` namespace was removed before release.

The first CIM-to-OCSF mapper covers Splunk CIM Network Resolution DNS events and
emits OCSF DNS Activity events.
