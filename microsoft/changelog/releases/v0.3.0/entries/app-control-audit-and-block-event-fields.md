---
title: App Control audit and block event fields
type: bugfix
authors:
  - zedoraps
created: 2026-11-18T10:40:12.142903Z
---

App Control audit and block events (3076/3077) now map the file, the loading process, and the signing levels. Windows reports them in `File Name`, `Process Name`, `Requested Signing Level`, and `Validated Signing Level`.

Sigma rules that read `FileNameBuffer`, `ProcessNameBuffer`, or the signing levels now see these values.
