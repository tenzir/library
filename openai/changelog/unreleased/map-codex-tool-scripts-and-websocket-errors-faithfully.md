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

- `exec` calls run a JavaScript tool script, so they no longer map to Process Activity for a process named `shell`. With `include_content=true` they map to Script Activity with the script text; without it they stay Base Events with the script hash in `unmapped`.
- Shell tool calls no longer set `process.name`, which Codex does not report; the tool name stays in `unmapped.tool_name`.
- Shell tool calls without a command no longer set `process.cmd_line` to an empty string.
- `error.message` maps to `status_detail`.
- `auth.request_id` of failed API requests maps to `api.request.uid`.
- Records without user attributes, such as model list requests and agent messages, no longer set an empty `actor.user`.
