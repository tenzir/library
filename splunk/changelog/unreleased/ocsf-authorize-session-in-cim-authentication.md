---
title: OCSF Authorize Session in CIM Authentication
type: feature
authors:
  - zedoraps
created: 2026-11-20T21:05:01.845101Z
---

OCSF Authorize Session, such as Windows 4672, maps to CIM Authentication with `tag=authentication`/`privileged`.

- `user` is the privileged account, `src_user` the actor or the same account.
- An audited 4672 success gives `action=success`; `dest_nt_domain` is the computer, `src_nt_domain` the account domain.
