---
title: Key-only account alert example for OpenSSH
type: feature
authors:
  - mavam
prs:
  - 223
created: 2026-11-06T09:11:16.60537Z
---

The `openssh` package now includes an example that flags successful password logins to accounts without a password, such as key-only users. Such a login points to an authentication bypass like CVE-2026-123158 or a misconfiguration. The example reads an account inventory of OCSF User objects keyed by `{host, user}` and alerts when the account carries the `key-only` label.
