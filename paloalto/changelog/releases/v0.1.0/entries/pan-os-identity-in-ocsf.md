---
title: Firewall, record, user, and endpoint context in PAN-OS OCSF events
type: change
authors:
  - zedoraps
created: 2026-11-20T17:56:57Z
---

PAN-OS OCSF events now name the firewall that logged them and carry a record UID and the management-plane receipt time, the User-ID source user becomes the actor, and more endpoint, HTTP response, and Threat context leaves `unmapped`.

**PAN-OS writes** (Traffic, abbreviated):

```
1,2026/05/29 17:00:01,000700000042,TRAFFIC,end,,2026/05/29 17:00:00,192.0.2.130,198.51.100.130,,,allow-web,example\carol,…,60,…,7701,…,tcp-fin,…,fw-example-1,…
```

**OCSF before → now:**

| | Before | Now |
|---|---|---|
| `metadata.reporter` | Not set; `unmapped.device_name` | `hostname: "fw-example-1"`, `uid: "000700000042"` |
| `metadata.uid` | Not set | `000700000042:TRAFFIC:7701` |
| `finding_info.uid` | Signature ID or bare sequence number | `metadata.uid` |
| `metadata.logged_time` | Receive time | High-resolution timestamp, such as `2026-05-29T17:00:01.250+02:00`, else the receive time |
| `duration` | Not set; `unmapped.elapsed_time` | `60000` |
| Device-ID OS and category, VM UUID | `unmapped` | `src_endpoint.os`, `type_id`, `instance_uid`, and the same for `dst_endpoint` |
| URL Filtering HTTP status code and content type | `unmapped` | `http_response.code`, `content_type` |
| Threat category, WildFire email sender, recipient, subject | `unmapped` | `finding_info.types`, `evidences[].email` |
| GlobalProtect host ID, client OS, error code | `unmapped` | `src_endpoint.uid`, `src_endpoint.os`, `status_code` |
| Decryption certificate fingerprint | `unmapped` | `tls.certificate.fingerprints` |
| Source user | `src_endpoint.owner.name: "example\carol"` | `actor.user`: `name: "carol"`, `domain: "example"` |
| Destination user | `dst_endpoint.owner.name: "example\svc"` | `dst_endpoint.owner`: `name: "svc"`, `domain: "example"` |
| GlobalProtect portal or gateway | `dst_endpoint.hostname` | `dst_endpoint.name` |
| `type`, `threat_content_type` of mapped records | Dropped | `unmapped` |

**What you need to do:** Update queries on the source user and the GlobalProtect gateway:

```tql
where actor.user.name == "carol" and actor.user.domain == "example"
where dst_endpoint.name == "example-external-gw"
```

**Why:** The device name is the hostname of the logging firewall, the high-resolution timestamp is when its management plane received the record, and PAN-OS numbers records per firewall and log type, so only all three identify a record. PAN-OS defines the source user as the user who initiated the session and writes users as `domain\user`. GlobalProtect portal and gateway columns hold configuration names, not hostnames.
