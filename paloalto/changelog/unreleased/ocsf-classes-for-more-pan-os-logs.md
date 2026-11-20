---
title: OCSF classes for PAN-OS authentication, configuration, DLP, decryption, correlation, and tunnel records
type: feature
authors:
  - zedoraps
created: 2026-11-20T17:56:57Z
---

`paloalto::ocsf::map` and `paloalto::ocsf::normalize` now map six more kinds of PAN-OS records to OCSF classes instead of Base Event.

**PAN-OS writes** (Authentication, Config, and GlobalProtect, abbreviated):

```
1,2026/05/29 19:00:01,000700000042,AUTHENTICATION,login,,2026/05/29 19:00:00,vsys1,192.0.2.140,example\dave,…,auth-fail,2,7802,…,RADIUS,…
1,2026/05/29 21:00:01,000700000042,CONFIG,0,,2026/05/29 21:00:00,192.0.2.160,vsys1,delete,admin-example,Web,Failed, vsys vsys1 rulebase security rules example-allow-web,…
1,2026/05/29 20:00:01,000700000042,GLOBALPROTECT,globalprotect,,2026/05/29 20:00:00,vsys1,gateway-connected,tunnel,…,192.0.2.151,…
```

**OCSF before → now:**

| PAN-OS records | Before | Now |
|---|---|---|
| Authentication (`AUTHENTICATION`, `AUTH`) | Base Event | Authentication (3002): user, source, service, policy, protocol, result, `is_mfa` for additional factors |
| GlobalProtect `portal-auth`, `gateway-auth` | Authentication for any `stage=login` | Authentication only for these event IDs, with IPv6 client fallback |
| GlobalProtect `gateway-connected`, `gateway-switch-to-ssl`, `gateway-logout` | Base Event | Tunnel Activity (4014): Open, Other, Close, with the tunnel address and login duration |
| Config | Base Event | Entity Management (3004): command as activity, configuration path as entity, change details before and after, administrator as actor; a commit's entity is the firewall's configuration |
| Data Filtering (`THREAT` `data`, `dlp`, `dlp-non-file`) | Base Event | Data Security Finding (2006): data pattern, DLP gateway, file, user, action |
| Decryption | Base Event | Network Activity (4001) with TLS version, SNI, server certificate, decryption policy; failure on handshake error |
| Correlated Events | Base Event with shifted fields | Detection Finding (2004): correlation object as analytic, evidence as description |

GlobalProtect prelogin, configuration, and host information records, as well as System, User-ID, HIP Match, IP-Tag, Tunnel Inspection, SCTP, and GTP records, stay Base Events with their parsed fields.

**What you need to do:** Queries on `class_uid == 0` for these records now need their class, for example:

```tql
where class_uid == 3004 and actor.user.name == "admin-example"
```

**Why:** Each of these PAN-OS logs describes an activity with an OCSF class. A record without a value that the class requires, such as an Authentication timeout without user, keeps the class and leaves the value missing.
