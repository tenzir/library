---
title: Exact OpenSSH timestamps
type: bugfix
authors:
  - zedoraps
created: 2026-11-21T14:35:22.862752Z
---

Timestamps are rounded to the microseconds that syslog writes, so a time such as `09:29:06.876067` no longer becomes `09:29:06.876066999` on some Tenzir versions.
