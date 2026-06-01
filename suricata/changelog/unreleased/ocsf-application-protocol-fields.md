---
title: OCSF application protocol fields
type: change
authors:
  - mavam
  - codex
prs:
  - 147
created: 2026-05-28T16:12:44.675386Z
---

The Suricata OCSF mapping now writes `app_proto` values and protocol-specific MQTT and SIP labels to OCSF 1.8's `app_protocol_name` field instead of `app_name`.
