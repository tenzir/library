---
title: Windows logon type, package, and domains in CIM
type: change
authors:
  - zedoraps
created: 2026-11-20T19:36:27.473315Z
---

Windows Security events report logon type, authentication package, and domains in CIM Authentication and Account Management.

- 4624/4625: the logon type number in `authentication_method` (`0` for System), the package in `authentication_service`.
- `dest_nt_domain`: the target account domain, the group domain, the caller computer for 4740, or the subject domain without a target; `-` stays empty.
- `src_nt_domain`: the subject domain, or the target domain for 4634.
- Domains can be authorities, such as `NT AUTHORITY`, or computer names.
