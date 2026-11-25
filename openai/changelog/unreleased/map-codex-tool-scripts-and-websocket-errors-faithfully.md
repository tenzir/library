---
title: Map Codex tool scripts and websocket errors faithfully
type: bugfix
authors:
  - zedoraps
components:
  - openai
created: 2026-11-25T23:26:07.623628Z
---

The Codex normalization no longer invents a process for `exec` tool scripts and keeps websocket error messages.

- `exec` calls run a JavaScript tool script, so they map to Base Event like other local tool calls instead of a Process Activity event for a process named `shell`.
- `error.message` maps to `status_detail`.
