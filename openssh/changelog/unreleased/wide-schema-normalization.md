---
title: One-schema OpenSSH normalization
type: change
authors:
  - zedoraps
created: 2026-08-26T00:00:00Z
---

`openssh::ocsf::normalize` now processes all `sshd` message templates on a
single wide schema and correlates authentication attempts on the collected
record list of each daemon process instead of expanding records through
per-window subpipelines. Events flow in large same-schema batches from the
parser to the mapper, and only the final OCSF event drops the unused fields.

On a replay of 22,300 Syslog records, normalization now spends about a tenth
of the previous CPU time and finishes about seven times faster end to end,
with identical OCSF output.

`openssh::parse` gains a `wide` option for this: `wide=true` keeps every
field of the union schema with `null`s in place of absent values, so all
messages share one schema. The default output shape is unchanged, and
`openssh::aggregate` now expects the wide form.
