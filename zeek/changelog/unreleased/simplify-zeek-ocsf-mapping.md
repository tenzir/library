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

The `zeek::ocsf::map` operator now owns the shared OCSF dispatch and
finalization for Zeek logs, replacing the former `zeek::ocsf::map_common`
helper. Event-specific OCSF operators focus on class-specific fields, and OCSF
tests now validate the mapper output with `ocsf::cast`.

The mapping now emits OCSF-shaped durations, DHCP lease durations, DNS TTLs,
FTP status codes, RDP device/display fields, SSH HASSH fingerprints, and X.509
certificate fingerprints.
