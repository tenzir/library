---
title: AppX deployment errors and packages
type: bugfix
authors:
  - zedoraps
created: 2026-11-18T10:40:13.693418Z
---

Failed AppX deployments (404) now report their error, and events that identify no package have no application.

| Field | Before | Now |
|---|---|---|
| `status_detail` of 404 | Not set | Error text from `SummaryError` |
| `application` without a package | Built from empty fields | Not set |
