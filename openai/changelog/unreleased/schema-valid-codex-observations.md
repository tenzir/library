---
title: Preserved Codex activities and source context
type: bugfix
authors:
  - zedoraps
created: 2026-10-28T11:20:36.711229Z
prs:
  - 208
---

Codex normalization now preserves the known OCSF class and activity when host or user context is missing. File operations remain File System Activity, and validation reports incomplete required fields as warnings.

Supply a real host identity through OpenTelemetry resource attributes, for example `OTEL_RESOURCE_ATTRIBUTES=host.name=workstation-42`. Missing or empty host identities produce actionable guidance at most once per normalizer instance without dropping events.

Optional requests and loggers are constructed only when identified. Email-only identity, unused request and turn identifiers, and host or model facts that were not mapped retain their original canonical keys in `unmapped`. Normalized events receive their OCSF schema names.
