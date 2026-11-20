---
title: Process IDs for Code Integrity actors
type: bugfix
authors:
  - zedoraps
created: 2026-11-19T00:53:52.382526Z
---

Code Integrity events now give the loading process in `actor.process` its process and thread ID. Code Integrity writes these events in the context of the loading process, so the event header carries its ID.

Before, `actor.process` had only a path, and `ocsf_cast` warned that an OCSF process needs a `pid`, `uid`, or `cpid`. Events without a header process ID keep the process name in `unmapped.EventData`.
