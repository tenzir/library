---
title: OpenSSH Syslog demo source
type: feature
authors:
  - zedoraps
prs:
  - 178
created: 2026-08-25T00:00:00Z
---

The new `demo::openssh` operator replays OpenSSH `sshd` Syslog captures from
six Linux distributions in real time. Pair it with the `openssh` package to
demonstrate parsing, correlation, and OCSF mapping without a live SSH server:

```tql
demo::openssh
where app_name in openssh::$app_names
openssh::ocsf::normalize
```
