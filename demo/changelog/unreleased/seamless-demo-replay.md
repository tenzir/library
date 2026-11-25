---
title: Seamless demo replay
type: breaking
authors:
  - zedoraps
prs:
  - 267
created: 2026-11-25T00:00:00Z
---

All demo feeds now replay without gaps, with current timestamps, and with new identifiers in every cycle:

- All feeds begin with the first event of their recording, share the arguments `speed` and `cycles`, and download the recording once.
- All feeds emit what the collector or reader emits: `demo::windows` parsed JSON or the XML in `data` instead of `time`, `format`, and `raw`, and the agent feeds `event.timestamp` as a string.
- `demo::zeek` and `demo::suricata` replay the same 20 minutes of an invented office with a small incident.
- `demo::replay::run`, `demo::replay::events`, and `demo::replay::renew_ids` replay your own short recordings.
- `demo::agents::read`, `demo::agents::rotate_ids`, and `demo::agents::shift_time` are gone. Use `demo::agents::replay` instead, which expects OTel records in JSON.
