---
title: Accurate status and activity in Zeek OCSF mappings
type: bugfix
authors:
  - zedoraps
created: 2026-11-25T23:30:31.629733Z
---

The Zeek mappings now report status, activity, and counts as the logs state them.

- TLS sessions with a completed handshake (`established: true`) have the status Success. `established` stays in `unmapped` when an alert decides the status.
- Email Activity events of a session without message data, such as a `221` reply after the envelope, have the status Unknown.
- SSH Activity events keep `auth_attempts` in `unmapped` instead of `count`.
- HTTP methods and FTP commands that OCSF does not list, such as `PASV`, map to activity Other with the source value in `activity_name`. HTTP Activity now maps the WebDAV methods that OCSF lists, such as `PROPFIND`.
- DNS records with only a query map to activity Query, and records with only a response map to activity Response with `response_time` instead of `query_time`.
