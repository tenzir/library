---
title: Agent findings from incomplete telemetry
type: bugfix
authors:
  - zedoraps
created: 2026-10-28T11:20:39.770073Z
prs:
  - 208
---

Agent detections continue to flag permissive modes, credential exposure, and hidden Unicode when host or user context is incomplete. The rules use the retained OCSF activity and preserve event time and agent context. Credential findings continue to withhold raw secrets.

Finding evidence retains observed agent and user details and emits typed identities only when the source identifies them. OCSF size profiles also work with the OCSF trimming function on Nova.
