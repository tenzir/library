---
title: Key-only account alert example for OpenSSH
type: feature
authors:
  - mavam
prs:
  - 223
created: 2026-11-06T09:11:16.60537Z
---

The `openssh` package now includes an example that flags successful password logins to accounts without a password, such as key-only users. Such a login points to an authentication bypass like CVE-2026-123158 or a misconfiguration. The package declares the `openssh-passwordless-accounts` lookup table, keyed by `{host, user}`, that the example checks.
