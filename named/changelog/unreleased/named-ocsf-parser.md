---
title: BIND named OCSF package
type: feature
authors:
  - raxyte
  - codex
prs:
  - 160
created: 2026-06-19T00:00:00Z
---

The library now includes a `named` package that normalizes ISC BIND `named`
messages to OCSF 1.9.

Use `named::ocsf::normalize` to take a record with `time` and a raw `message`
body all the way to OCSF. The normalizer preserves the body in `raw_data`. Use
`named::parse` and `named::ocsf::map` with separate input and output fields when
a pipeline needs to inspect or enrich the structured BIND event before mapping.

The package expands common query logging templates, including regular queries,
view-qualified queries, query failures, and cache/client query denials. Other
`named` daemon, zone, resolver, and DNSSEC diagnostics become OCSF Base Event
records for downstream routing and inspection. Parser diagnostics remain in the
mapped event's `unmapped` object instead of appearing as DNS activity failures.
