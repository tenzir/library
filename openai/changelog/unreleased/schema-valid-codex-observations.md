---
title: Schema-valid Codex observations
type: bugfix
authors:
  - zedoraps
created: 2026-10-28T11:20:36.711229Z
prs:
  - 208
---

Codex normalization now emits schema-valid OCSF events when telemetry omits a user, host, logger name, or request identifier. Incomplete request and logger details remain in unmapped data. Activities that require an unavailable host or user become Base Events with their original mapping preserved under `unmapped.incomplete_activity`.

OpenTelemetry resource attributes `host.name` and `host.id` now identify the device for file and process activity. Operations with reported host context retain their specific OCSF class and activity, including file renames.
