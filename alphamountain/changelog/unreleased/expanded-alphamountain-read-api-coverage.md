---
title: Expanded alphaMountain read API coverage
type: feature
authors:
  - mavam
  - codex
created: 2026-06-15T00:00:00Z
---

The alphaMountain package now includes read operators for multi-URI category
and threat lookups, plus license and service quota information.

Lookup and feed operators now expose single-service API statuses as plain
`status` strings, while the OCSF mapper moves shaped API status and error
details into OCSF status fields.
