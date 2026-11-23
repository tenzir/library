---
title: More Check Point fields mapped to OCSF
type: change
authors:
  - zedoraps
created: 2026-11-23T14:36:28.382184Z
---

The `checkpoint` package maps more Check Point fields to OCSF and stops deriving values the source doesn't state:

- **Remote access VPN logins** now carry the client's MAC address, operating system edition, build, and bitness, the device identifier and host type, the VPN client as an agent, the session creation time, and the authentication factors with `is_mfa`.
- **Identity Awareness logins** list the user's groups in `user.groups`.
- **Network events** map TCP flags to `connection_info.tcp_flags`, prefer the security zone for `src_endpoint.zone` and `dst_endpoint.zone`, and set `status_detail` from the reason of the outcome. A record that names a service without a destination address now gets a `dst_endpoint`.
- **Parsing** strips the trailing colon from keys such as `scheme:` and trims spaces around user names.
- **Scan Activity** no longer computes `start_time` and `end_time` from the record time, and `seconds` is no longer read as `duration`. Both values remain available, `seconds` under `unmapped`.
