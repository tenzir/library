---
title: OCSF application protocol fields
type: change
authors:
  - mavam
  - codex
prs:
  - 147
created: 2026-05-28T16:12:37.224993Z
---

The Zeek OCSF mapping now writes the protocol identified by Zeek, such as `http`, to OCSF 1.8's `app_protocol_name` field instead of `app_name`.
