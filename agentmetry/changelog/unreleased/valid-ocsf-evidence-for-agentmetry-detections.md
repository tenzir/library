---
title: Valid OCSF evidence for Agentmetry detections
type: bugfix
authors:
  - mavam
prs:
  - 225
created: 2026-11-10T08:15:02.158022Z
---

Agentmetry detection evidence now includes the identified acting user alongside the AI agent, satisfying OCSF 1.9's evidence constraint. When no acting user is identified, the agent remains under `unmapped.agent` rather than producing invalid evidence. Actor-only detections also retain their evidence.
