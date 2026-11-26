---
title: Map Codex tool scripts and websocket errors faithfully
type: bugfix
authors:
  - zedoraps
components:
  - openai
created: 2026-11-25T23:26:07.623628Z
---

The Codex normalization no longer invents processes for tool calls and keeps websocket error messages.

- `exec` calls run a JavaScript tool script, so they map to Script Activity instead of a Process Activity event for a process named `shell`.
- Shell tool calls no longer set `process.name`, which Codex does not report; the tool name stays in `unmapped.tool_name`.
- `error.message` maps to `status_detail`.
