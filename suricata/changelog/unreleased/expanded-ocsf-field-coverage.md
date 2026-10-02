---
title: Expanded OCSF 1.9 field coverage
type: change
authors:
  - mavam
prs:
  - 191
created: 2026-10-02T14:34:35.871905Z
---

Suricata OCSF events now expose DNS header IDs, flags and record sections; TCP header flags; certificate creation times and SANs; JA4 fingerprints; SSH implementations; and file hashes and descriptions. Application transaction counters, raw DNS flags, and unsupported protocol context remain in `unmapped`.
