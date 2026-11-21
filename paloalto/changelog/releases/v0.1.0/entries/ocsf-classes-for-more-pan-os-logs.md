---
title: OCSF classes for PAN-OS authentication, configuration, DLP, decryption, correlation, and tunnel records
type: feature
authors:
  - zedoraps
created: 2026-11-20T17:56:57Z
---

`paloalto::ocsf::map` and `paloalto::ocsf::normalize` now map six more kinds of PAN-OS records to OCSF classes instead of Base Event:

- **Authentication** (`AUTHENTICATION`, `AUTH`) → Authentication (3002) with user, source, service, policy, protocol, result, and `is_mfa` for additional factors.
- **GlobalProtect** `portal-auth` and `gateway-auth` → Authentication, now only for these event IDs; `gateway-connected`, `gateway-switch-to-ssl`, and `gateway-logout` → Tunnel Activity (4014) with the tunnel address and login duration.
- **Config** → Entity Management (3004): the command as activity, the configuration path as entity with the change details, the administrator as actor; a commit's entity is the firewall's configuration.
- **Data Filtering** → Data Security Finding (2006) with data pattern, file, user, and action.
- **Decryption** → Network Activity (4001) with TLS version, SNI, server certificate, and decryption policy.
- **Correlated Events** → Detection Finding (2004) with the correlation object and evidence.

Other GlobalProtect records and System, User-ID, HIP Match, IP-Tag, Tunnel Inspection, SCTP, and GTP records stay Base Events.
