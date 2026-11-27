---
title: Accurate OpenSSH logins and forward requests
type: bugfix
authors:
  - zedoraps
created: 2026-11-25T23:32:19.003517Z
---

The OpenSSH normalization maps more logins, forward requests, and credentials correctly:

- Records with the same timestamp now keep their log order, so a login on a host that logs whole seconds keeps its key evidence, MFA status, and destination endpoint.
- A denied forward request names the requested target in `dst_endpoint` without `sshd` as its service, and sets `connection_info.direction_id` to Unknown.
- Authentication events no longer set the deprecated `user.credential_uid`; the public key type and fingerprint stay in `unmapped.credential`. Network Activity events drop the deprecated `is_src_dst_assignment_known`.
