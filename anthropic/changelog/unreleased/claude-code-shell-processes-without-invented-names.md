---
title: Claude Code shell processes without invented names
type: bugfix
authors:
  - zedoraps
components:
  - anthropic
created: 2026-11-26T00:43:34.487151Z
---

The Claude Code normalization no longer invents process names or empty command lines.

- Bash tool calls no longer set `process.name` to `bash`, which Claude Code does not report; the tool name stays in `unmapped.tool_name`.
- Tools that Claude Code does not ship, such as `exec` or `shell`, no longer map to Process Activity.
- Hook processes and shell tool calls without a command no longer set `process.cmd_line` to an empty string.
