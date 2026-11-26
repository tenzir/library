---
title: S3 example moves objects within the bucket
type: bugfix
authors:
  - zedoraps
prs:
  - 276
created: 2026-11-26T17:41:27.116477Z
---

The S3 example now moves read objects to `processed/harfanglab/` in the same
bucket instead of to a nonexistent bucket named `processed`.
