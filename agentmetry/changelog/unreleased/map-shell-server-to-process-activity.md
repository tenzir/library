---
title: Map Agentmetry shell calls from recorded tool names
type: bugfix
authors:
  - blitzcrieg1
created: 2026-11-06T12:00:00.000000Z
---

Agentmetry records the shell calls of Codex and Cursor under server `shell`,
for example as tool `run`, and those of Antigravity as `run_command`. These now
map to Process Activity instead of API Activity, including inferred approval
responses. A tool named `run` on another server stays API Activity.
