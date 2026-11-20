---
title: App Control audit and block event fields
type: bugfix
authors:
  - zedoraps
created: 2026-11-18T10:40:12.142903Z
---

App Control audit and block events (3076/3077) now map the file, the loading process, and the signing levels.

| Field | Before | Now |
|---|---|---|
| `application.name`, `application.data.file_path` | Empty | From `File Name` |
| `actor.process` | Missing | From `Process Name` |
| `application.data.requested_signing_level`, `validated_signing_level` | Empty | From `Requested Signing Level`, `Validated Signing Level` |

Sigma rules that read `FileNameBuffer`, `ProcessNameBuffer`, or the signing levels now see these values.
