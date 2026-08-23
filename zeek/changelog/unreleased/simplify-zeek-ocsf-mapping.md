---
title: Simplify Zeek OCSF mapping
type: change
authors:
  - mavam
  - codex
prs:
  - 147
created: 2026-05-31T16:29:33Z
---

Zeek normalization now owns shared OCSF dispatch and finalization. Event-specific
OCSF operators focus on class-specific fields. OCSF tests validate the minimal normalized output with `ocsf_cast`.

The mapping now emits OCSF-shaped durations, DHCP lease durations, DNS TTLs,
FTP status codes, RDP device/display fields, SSH HASSH fingerprints, and X.509
certificate fingerprints.
