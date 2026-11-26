---
title: Correct Zeek connection status, DHCP UIDs and domains, and HTTP profiles
type: bugfix
authors:
  - zedoraps
created: 2026-11-26T01:38:20.321286Z
---

The Zeek OCSF mappings correct a few attributes:

- Network Activity from `conn.log` names the connection state, such as `SF`, in `status` instead of `Other`.
- DHCP Activity sets `metadata.correlation_uid` only for a single connection and keeps several UIDs in `unmapped.uids`. The domain of option 15 moves from `dst_endpoint` to `src_endpoint`.
- HTTP Activity declares the `host` profile only for requests with a user name.
