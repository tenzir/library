---
title: Claude Code and Codex demo sources
type: feature
authors:
  - zedoraps
prs:
  - 187
created: 2026-09-14T14:53:40.379029Z
---

The new `demo::claude_code` and `demo::codex` operators continuously replay
public, anonymized agent telemetry without a local dataset or a live agent:

```tql
demo::claude_code
anthropic::claude_code::ocsf::normalize include_content=true
```

Use `demo::codex` with `openai::codex::ocsf::normalize` for Codex. Each source
averages about one event per second by default while retaining bursts and
pauses. Set `speed=2.0` to double that rate. Each replay cycle uses current
timestamps and fresh correlation IDs, preserving related references and fixed
ID prefixes.
