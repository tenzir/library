---
title: Enumeration actors, Defender IDs, and firewall service states
type: change
authors:
  - zedoraps
prs:
  - 261
created: 2026-11-22T12:00:12.317836Z
---

More Windows details map to OCSF:

- 4797–4799: the subject as `actor`, and the caller process for 4798/4799.
- Defender 1116/1117: the threat ID in `malware[].uid`, and the platform version in `metadata.product.version`.
- Firewall and IPsec service events 5025, 5030, 5034, 5035, and 5478: Application Lifecycle instead of Base Event. 5033 names the same `Windows Firewall Driver` as 5034 and 5035.
- Account, group, scheduled task, registry, permission, enumeration, and special privilege events, such as 4720, 4728, 4698, 4657, 4670, 4799, and 4672: `status_id` from the audit keywords. Sysmon 12–14 get Success.
- Group membership changes: the common name of a distinguished member name in `users[].name`, such as `carol` for `CN=carol,CN=Users,DC=example,DC=test`, and the full name in `users[].ldap_person.ldap_dn`.
- Scheduled tasks 4698–4702: the command and arguments of the first task action in `job.cmd_line`.
- 4769: the KDC in `dst_endpoint.hostname`, as for 4768. 1100, 1107, and 1108: the `Event Logging Service` as `actor.app_name`.
