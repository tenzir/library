---
title: Preserved Claude Code activities and source context
type: bugfix
authors:
  - zedoraps
created: 2026-10-28T11:20:32.144092Z
prs:
  - 208
---

Claude Code normalization now preserves the known OCSF class and activity when host or user context is missing. File renames remain File System Activity/Rename, and validation reports incomplete required fields as warnings.

Supply a real host identity through OpenTelemetry resource attributes, for example `OTEL_RESOURCE_ATTRIBUTES=host.name=workstation-42`. Missing or empty host identities produce actionable guidance at most once per normalizer instance without dropping events.

Optional requests and loggers are constructed only when identified. Email-only identity, unused request identifiers, and host or model facts that were not mapped retain their original canonical keys in `unmapped`. Normalized events receive their OCSF schema names.
