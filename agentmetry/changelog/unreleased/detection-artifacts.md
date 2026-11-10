---
title: Map Agentmetry detection artifacts to evidence
type: feature
authors:
  - blitzcrieg1
created: 2026-11-10T00:00:00.000000Z
---

Detection findings with optional `detection.artifacts` version 1 now promote
named tool observations into API evidence, captured paths on recognized file
tools into file evidence, and captured URLs into URL evidence. Each entry keeps
its source event ID without inheriting the triggering actor or inventing a
process identity. File type remains Unknown.

The complete artifact block stays under `unmapped`, including reported outcomes,
source sessions, inference markers and omission counts. Gate-only snapshots and
unknown versions stay unmapped. Old findings without artifacts keep their
existing mapping. The package description also clarifies that the standalone
Agentmetry hook requires explicit opt-in for command and full-argument capture.
