---
title: Windows events in more CIM datasets
type: feature
authors:
  - zedoraps
prs:
  - 261
created: 2026-11-22T12:00:09.100572Z
---

More Windows events map to the CIM dataset that fits them instead of passing through or landing in Alerts:

- Authentication: OCSF Authorize Session, such as 4672, with the tag `privileged`.
- Endpoint Registry: registry key and value activity, such as Sysmon 12/13 and 4657, and 4670 on registry keys.
- Endpoint Services: service activity, such as 4697, 7045, and 7040, and service state, such as 7036, 7034, 7023, 5024, 5025, and 1100.
- Change: scheduled job changes, such as 4698–4702; account and group enumerations (4797–4799) with `action=read`, where 4799 stays out of Account Management and names the querying account as `user`; 4670 on other objects with `action=acl_modified`.
- Malware: Defender detections (1116/1117) in Malware Attacks and configuration changes (5007) in Malware Operations.
