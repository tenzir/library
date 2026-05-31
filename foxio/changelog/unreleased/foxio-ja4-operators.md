---
title: FoxIO JA4 operators
type: feature
authors:
  - mavam
  - codex
prs:
  - 147
created: 2026-05-31T19:12:55Z
---

The FoxIO package now exposes JA4+ enrichment as reusable operators.

Use `foxio::ocsf::map` to turn JA4+ fingerprint records into OCSF OSINT
Inventory Info events that can be joined with network telemetry.

The old public JA4DB download workflow is marked as unavailable because the
legacy endpoint no longer appears to be publicly accessible.
