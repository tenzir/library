---
title: Required OCSF attributes in Suricata events
type: bugfix
authors:
  - zedoraps
prs:
  - 205
created: 2026-10-20T14:30:39.259989Z
---

Suricata events from `suricata::ocsf::normalize` now include all attributes
that OCSF 1.9 marks as required, so strict OCSF validators accept them.

- `connection_info.direction_id` is now `0` (Unknown), also inside alert
  evidence, because Suricata does not know whether a flow is inbound,
  outbound, or lateral.
- SMB events with server OS details now carry `device.type_id: 0` (Unknown).
- Network File Activity events from `fileinfo` records now include an empty
  `actor`, because Suricata does not record who transferred the file.
- TLS events only include `tls.certificate` when Suricata logged both the
  issuer and serial number, and only include `ja3_hash`, `ja3s_hash`, and
  certificate fingerprints when they have a value. Previously, resumed
  sessions produced certificates and fingerprints without their required
  fields.
