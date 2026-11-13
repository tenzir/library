---
title: Reported results and invocation IDs for Agentmetry tool calls
type: feature
authors:
  - blitzcrieg1
  - mavam
prs:
  - 229
created: 2026-11-13T00:00:00.000000Z
---

Agentmetry tool calls from Claude Code now carry what the harness reported
about each call. The tool-use ID that links a request to its result becomes
`process.uid` of a shell call and `api.request.uid` of an API call, so a shell
call from Claude Code no longer triggers the OCSF warning about a process
without identity. A result's reported status becomes `status_code` and its
reported execution time becomes `duration`, including a duration of zero.
Neither proves that the tool ran or how it ended, so the outcome still decides
`status_id`.
