---
title: OCSF network detection operators
type: feature
authors:
  - mavam
  - codex
prs:
  - 172
created: 2026-08-07T20:53:58.221185Z
---

The `tenzir` package now turns OCSF Network Activity streams into Detection
Findings for scan fan-out, beacon cadence, long connections, and outbound volume
bursts.

Run any detector as a user-defined operator between your normalized stream and
the findings topic:

```tql
subscribe "ocsf"
tenzir::detect::beacon_cadence
publish "findings"
```

Each operator exposes its time window, late-event tolerance, and detection
thresholds as named arguments for environment-specific tuning.

The beacon and volume detectors measure originator traffic via
`traffic.bytes_out`, the source-to-destination byte count that the NetFlow,
Zeek, and Suricata mappings populate consistently.
