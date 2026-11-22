---
title: Corrected CIM field values
type: change
authors:
  - zedoraps
prs:
  - 261
created: 2026-11-22T12:00:09.949838Z
---

`splunk::cim::from_ocsf` fills several CIM fields more accurately:

- Authentication: the Windows logon type in `authentication_method`, the package in `authentication_service`, and the target session in `session_id`. `dest_nt_domain` and `src_nt_domain` follow the target and subject. `user_role` and `src_user_role` are gone, since they copied the user type. Logoffs no longer count as sign-ins, and audited 4648 logons count as successful privileged authentication.
- Processes: `action` reports the endpoint decision instead of the lifecycle, so `action=launch` becomes `action=allowed`. `user` is the creator, and `original_file_name` is filled.
- Change and Filesystem: `action` uses CIM values such as `cleared` and `modified`, and group events list all members in `user`, `user_name`, and `user_type`.
- Network Traffic: the actor user and process.
- ID-only OCSF gets its captions derived, so it maps like derived OCSF.
