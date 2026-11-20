---
title: Application crash fields as Windows writes them
type: bugfix
authors:
  - zedoraps
created: 2026-11-18T10:40:09.905177Z
---

Application crashes (1000) now map the values that Windows writes, with or without field names.

| Field | Before | Now |
|---|---|---|
| `module.file` | Positional data only | Also `ModuleName`, `ModulePath` |
| `module.load_type_id` | Not set | `0` (Unknown) |
| `actor.process` | Not set | The crashed process |
| `process.pid` without hex letters, such as `2048` | Read as decimal | Read as hexadecimal |
