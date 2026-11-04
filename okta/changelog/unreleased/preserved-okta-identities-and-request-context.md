---
title: Preserved Okta identities and request context
type: bugfix
created: 2026-11-04T15:46:59.061701Z
---

Okta events now retain unmapped actor, request, client, and target details under their original source keys. Authentication request identifiers no longer appear as URL hostnames, and missing optional context no longer creates empty OCSF objects.

New-user events retain the reported user identity. System principals and client applications use their matching OCSF actor types, while a client reported only as `Computer` keeps its device type Unknown.
