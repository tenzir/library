---
title: Preserve inferred Agentmetry approval outcomes
type: bugfix
authors:
  - blitzcrieg1
created: 2026-11-05T17:50:00.000000Z
---

An Agentmetry approval response inferred from a subsequent tool call now
keeps its reason and maps to Unknown disposition. A session that ends with
a pending request also keeps its inferred reason and Unknown disposition.
Qualified built-in shell tool names such as `codex.exec_command` map to
Process Activity.
