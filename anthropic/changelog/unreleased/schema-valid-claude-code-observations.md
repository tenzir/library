---
title: Schema-valid Claude Code observations
type: bugfix
authors:
  - zedoraps
created: 2026-10-28T11:20:32.144092Z
prs:
  - 208
---

Claude Code normalization now emits schema-valid OCSF events when telemetry omits a user, host, logger name, or request identifier. Incomplete request and logger details remain in unmapped data. Activities that require an unavailable host or user become Base Events with their original mapping preserved under `unmapped.incomplete_activity`.
