---
title: Firewall, record, user, and endpoint context in PAN-OS OCSF events
type: change
authors:
  - zedoraps
created: 2026-11-20T17:56:57Z
---

PAN-OS OCSF events now identify the firewall, the record, and the user, and map more source context.

- `metadata.reporter` names the firewall (`hostname`, serial as `uid`), and `metadata.uid` is serial, log type, and sequence number, such as `000700000042:TRAFFIC:7701`; findings use it as `finding_info.uid`.
- `metadata.logged_time` is the high-resolution timestamp, else the receive time; Traffic sessions get `duration`.
- The source user becomes `actor.user` and the destination user `dst_endpoint.owner`, with `example\carol` split into domain `example` and name `carol`.
- GlobalProtect portals and gateways become `dst_endpoint.name` instead of a hostname.
- Device-ID OS and category and VM UUIDs become endpoint `os`, `type_id`, and `instance_uid`; GlobalProtect host ID, client OS, and error code become `src_endpoint.uid`, `src_endpoint.os`, and `status_code`.
- URL Filtering status code and content type become `http_response`, threat categories `finding_info.types`, WildFire email details `evidences[].email`, and certificate fingerprints `tls.certificate.fingerprints`.
- Mapped records keep their log type and subtype in `unmapped`.
