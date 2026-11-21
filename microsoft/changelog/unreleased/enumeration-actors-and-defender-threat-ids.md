---
title: Enumeration actors and Defender threat IDs
type: change
authors:
  - zedoraps
created: 2026-11-21T11:35:40.337746Z
---

Account and group enumerations name who queried, and Defender events keep the threat ID and platform version.

- 4797/4798/4799: `actor` with the subject account and logon ID, and the caller process for 4798/4799.
- 4798: the enumerated SID (`TargetSid`) in `query_evidence.user.uid`.
- Defender 1116/1117: the threat ID in `malware[].uid`; detections and protection changes: the platform version in `metadata.product.version`.
