---
title: Required OCSF attributes in OpenSSH events
type: bugfix
authors:
  - zedoraps
created: 2026-10-20T14:30:38.281761Z
---

OpenSSH events from `openssh::ocsf::normalize` now include all attributes that
OCSF 1.9 marks as required, so strict OCSF validators accept them.

Every event with a `device` now carries `device.type_id: 0` (Unknown).
Authentication events that sshd logged before learning the login name now
include an empty `user` object instead of omitting `user`.
