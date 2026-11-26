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
bucket. Before, its `rename` lambda prefixed the path with `processed/`, but
the path starts with the bucket name, so it targeted a bucket named
`processed`.
