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

The library now includes a `named` package with `named::parse` and
`named::ocsf::map` for parsing ISC BIND `named` log message bodies and mapping
the normalized records to OCSF.

The package currently expands common query logging templates, including regular
queries, view-qualified queries, query failures, and cache/client query denials.
Other `named` daemon, zone, resolver, and DNSSEC diagnostics are retained as OCSF
Base Event records for downstream routing and inspection.

The parser expects input records with required `time` and raw `message` fields.
The raw message body is preserved as `raw_data`; parser diagnostics are kept in
the mapped event's `unmapped` object instead of being reported as DNS activity
failures.
