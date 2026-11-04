---
title: OpenSSH identity retention and optional source endpoints
type: bugfix
prs:
  - 213
created: 2026-11-04T14:41:26.876782Z
---

Correlated OpenSSH authentication failures now retain the user reported by companion records when the selected PAM message omits it and the attempt names a single user. Network errors without a peer address no longer emit an empty source endpoint, so these events pass OCSF validation.
