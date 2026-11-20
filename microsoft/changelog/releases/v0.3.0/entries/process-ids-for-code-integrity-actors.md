---
title: Process IDs for Code Integrity actors
type: bugfix
authors:
  - zedoraps
created: 2026-11-19T00:53:52.382526Z
---

Code Integrity events now give the loading process its process and thread ID.

| Field | Before | Now |
|---|---|---|
| `actor.process.pid`, `ptid` | Not set | From the event header |
| `actor.process` without a header process ID | Path only | Not set; the name stays in `unmapped.EventData` |

**Why:** Code Integrity writes these events in the context of the loading process, and an OCSF process needs a `pid`, `uid`, or `cpid`.
