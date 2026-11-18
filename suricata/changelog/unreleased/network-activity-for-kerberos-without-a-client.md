---
title: Network Activity for Kerberos without a client
type: change
authors:
  - zedoraps
created: 2026-11-18T10:12:10.688416Z
---

Kerberos events without a client principal now map to Network Activity instead of Authentication, which requires the authenticated user. This affects TGS requests, whose client identity is encrypted, errors without a client name, and AS requests that omit one, such as scanner probes. The message type, service principal, realm, and failed request remain under `unmapped.krb5`, and errors keep their code in `status_code`. Kerberos events that name a client still map to Authentication.
