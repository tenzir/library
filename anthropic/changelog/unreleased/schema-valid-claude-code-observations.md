---
title: Schema-valid Claude Code observations
type: bugfix
authors:
  - zedoraps
created: 2026-10-28T11:20:32.144092Z
prs:
  - 208
---

Claude Code normalization now emits schema-valid OCSF events when telemetry omits a user, host, logger name, or request identifier. Incomplete request and logger details remain in unmapped data. Activities that require an unavailable host or user become Base Events with their remaining fields retained directly in `unmapped`.

OpenTelemetry resource attributes `host.name` and `host.id` now identify the device for file and process activity. Operations with reported host context retain their specific OCSF class and activity, including file renames.

Missing host identity now emits a warning explaining how to supply `host.name` or `host.id` through OpenTelemetry resource attributes. The event is retained, and the warning is emitted at most once per normalizer instance.
