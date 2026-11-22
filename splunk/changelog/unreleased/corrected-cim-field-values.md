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

- Authentication: `signature` is the event title from the OCSF `message`, such as `An account was successfully logged on`. Windows logons get the logon type in `authentication_method`, the package in `authentication_service`, `app=win:local`, `win:remote`, or `win:unknown`, and the logon ID as `session_id`, so a logon and its logoff share it. `dest_nt_domain` and `src_nt_domain` follow the target and subject, and 4769 gets the KDC as `dest`. `user_role` and `src_user_role` are gone, since they copied the user type. Logoffs no longer count as sign-ins, and audited 4648 logons count as successful privileged authentication.
- Processes: `action` reports the endpoint decision instead of the lifecycle, so `action=launch` becomes `action=allowed`. `user` is the account the process runs as, such as the 4688 target account, and `original_file_name` is filled. `parent_process` falls back to the parent path.
- Change and Filesystem: `action` uses CIM values such as `cleared` and `modified`, and group events list all members in `user`, `user_name`, and `user_type`.
- Account Management: `action` is `created`, `deleted`, `lockout`, `unlocked`, or `modified` instead of the OCSF activity name, such as `add_user`. Membership changes name the member in `object` with `object_category=user` and the group in `object_attrs`.
- Change and Endpoint Registry: `status` comes from the OCSF status. Registry events get `registry_hive`, and scheduled tasks the `command`.
- Network Traffic: the actor user and process. Connections without a decision get `action=allowed` instead of `open`, `protocol=ip` with `protocol_version` `ipv4` or `ipv6`, and the process as `app`.
- ID-only OCSF gets its captions derived, so it maps like derived OCSF.
