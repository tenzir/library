---
title: Microsecond Zeek timestamps
type: bugfix
authors:
  - zedoraps
prs:
  - 242
created: 2026-11-18T09:21:56.030167Z
---

Zeek events report their time and SMB file times with the microsecond precision that Zeek logs. Readers previously added floating-point noise below the microsecond, which differed between Tenzir versions, so the same Zeek log could normalize to slightly different times and notice finding UIDs.
