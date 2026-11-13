---
title: Reported results and invocation IDs for Agentmetry tool calls
type: feature
authors:
  - blitzcrieg1
created: 2026-11-13T00:00:00.000000Z
---

Agentmetry tool calls from Claude Code now carry what the harness reported
about each call. A result's reported status becomes `status_code` and its
reported execution time becomes `duration`, including a duration of zero. The
tool-use ID that links a request to its result stays under
`unmapped.tool.invocation`, together with its provenance. Neither the status
nor the duration proves that a process ran or how it exited.
