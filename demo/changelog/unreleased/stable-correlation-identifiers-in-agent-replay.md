---
title: Stable correlation identifiers in agent replay
type: bugfix
authors:
  - zedoraps
prs:
  - 200
created: 2026-10-28T18:30:52.159697Z
---

Claude Code and Codex demo replays now keep rotated correlation identifiers as strings, even when a generated identifier resembles a duration. This prevents intermittent replay warnings and lost events while retaining matching references across the capture. Replay timestamps still shift to the requested timeline.
