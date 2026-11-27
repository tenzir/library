---
title: Ongoing ingress throughput for demo feeds
type: bugfix
authors:
  - mavam
prs:
  - 280
created: 2026-11-27T14:42:06.270582Z
---

Replayed events from `demo::zeek`, `demo::suricata`, `demo::openssh`, `demo::windows`, `demo::claude_code`, and `demo::codex` now report ongoing ingress event throughput instead of dropping to zero after the initial download. Each feed still downloads its recording once at startup without inflating ingress byte counts.
