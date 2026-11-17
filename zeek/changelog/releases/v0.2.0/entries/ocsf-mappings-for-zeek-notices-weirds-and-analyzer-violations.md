---
title: OCSF mappings for Zeek notices, weirds, and analyzer violations
type: feature
authors:
  - zedoraps
created: 2026-11-17T11:16:01.752549Z
---

Zeek's own detections from `notice.log` become OCSF Detection Findings. Each finding carries the notice type as its title and analytic, the message as its description, the endpoints and transferred files as evidence, and the MITRE ATT&CK techniques that ATT&CK notices list.

Protocol anomalies from `weird.log` and analyzer violations from `analyzer.log` become Network Activity events with their endpoints and the anomaly or violation text as `message`, so you can find them by IP address and port like other connection events. Records without a connection stay Base Events.
