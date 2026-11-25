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

- All feeds share the arguments `speed`, `start`, `seed`, `cycles`, and `pace`, and download their recording once.
- `demo::zeek` and `demo::suricata` replay samples that ship with the package.
- `demo::replay::run`, `demo::replay::mark`, `demo::openssh::replay`, and `demo::windows::replay` are new.
- `demo::agents::rotate_ids` and `demo::agents::shift_time` are gone. Use `demo::agents::replay` instead.
