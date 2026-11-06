---
title: RFC 3164 Syslog for OpenSSH normalization
type: bugfix
authors:
  - mavam
prs:
  - 223
created: 2026-11-06T09:11:16.382179Z
---

The `openssh::ocsf::normalize` operator now maps RFC 3164 Syslog events as parsed by `read_syslog`, without renaming `content` to `message` or parsing the timestamp first. Classic BSD Syslog, the default on Alpine and other BusyBox systems, previously produced field warnings and no OCSF events. Year-less timestamps resolve against the processing time.
