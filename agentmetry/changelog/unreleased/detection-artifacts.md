---
title: Evidence from the tool calls behind Agentmetry detections
type: feature
authors:
  - blitzcrieg1
prs:
  - 227
created: 2026-11-10T00:00:00.000000Z
---

Agentmetry detection findings now show the tool calls that triggered them as
OCSF evidence, provided the Agentmetry version attaches them. Each call
appears with its event ID and tool name, plus the file path or URL when
Agentmetry captured one, so you can see what the agent touched without looking
up the original events.
