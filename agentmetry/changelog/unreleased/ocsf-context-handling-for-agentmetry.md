---
title: OCSF context handling for Agentmetry
type: bugfix
created: 2026-11-04T14:57:22.654089Z
---

Agentmetry normalization now sets `device.type_id` to Unknown for reported hosts and creates optional actor, analytic, and endpoint objects only when the source identifies them. Actor details without an ID remain under their original keys in `unmapped`.
