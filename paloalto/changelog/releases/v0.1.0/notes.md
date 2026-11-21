The Palo Alto Networks package now parses PAN-OS records exactly as the firewall writes them, across more PAN-OS versions, layouts, and time zones. Its OCSF mappings normalize actions, outcomes, and identities consistently and map six more kinds of PAN-OS records to OCSF classes.

## 🚀 Features

### OCSF classes for PAN-OS authentication, configuration, DLP, decryption, correlation, and tunnel records

`paloalto::ocsf::map` and `paloalto::ocsf::normalize` now map six more kinds of PAN-OS records to OCSF classes instead of Base Event:

- **Authentication** (`AUTHENTICATION`, `AUTH`) → Authentication (3002) with user, source, service, policy, protocol, result, and `is_mfa` for additional factors.
- **GlobalProtect** `portal-auth` and `gateway-auth` → Authentication, now only for these event IDs; `gateway-connected`, `gateway-switch-to-ssl`, and `gateway-logout` → Tunnel Activity (4014) with the tunnel address and login duration.
- **Config** → Entity Management (3004): the command as activity, the configuration path as entity with the change details, the administrator as actor; a commit's entity is the firewall's configuration.
- **Data Filtering** → Data Security Finding (2006) with data pattern, file, user, and action.
- **Decryption** → Network Activity (4001) with TLS version, SNI, server certificate, and decryption policy.
- **Correlated Events** → Detection Finding (2004) with the correlation object and evidence.

Other GlobalProtect records and System, User-ID, HIP Match, IP-Tag, Tunnel Inspection, SCTP, and GTP records stay Base Events.

*By @zedoraps.*

### Time zone of PAN-OS times

PAN-OS times without a zone are now interpreted in the zone of the new optional `timezone` argument of `paloalto::parse` and `paloalto::ocsf::normalize`, such as `timezone="Europe/Berlin"`, else in the offset of the record's high-resolution timestamp, and only then in UTC.

*By @zedoraps.*

## 🔧 Changes

### Expanded OCSF 1.9 field coverage

PAN-OS OCSF events now expose sequence numbers, endpoint locations and users, and session-end reasons. Country codes become endpoint locations, while country names and other vendor-specific context remain in `unmapped`.

*By @mavam in #191.*

### Firewall, record, user, and endpoint context in PAN-OS OCSF events

PAN-OS OCSF events now identify the firewall, the record, and the user, and map more source context.

- `metadata.reporter` names the firewall (`hostname`, serial as `uid`), and `metadata.uid` is serial, log type, and sequence number, such as `000700000042:TRAFFIC:7701`; findings use it as `finding_info.uid`.
- `metadata.logged_time` is the high-resolution timestamp, else the receive time; Traffic sessions get `duration`.
- The source user becomes `actor.user` and the destination user `dst_endpoint.owner`, with `example\carol` split into domain `example` and name `carol`.
- GlobalProtect portals and gateways become `dst_endpoint.name` instead of a hostname.
- Device-ID OS and category and VM UUIDs become endpoint `os`, `type_id`, and `instance_uid`; GlobalProtect host ID, client OS, and error code become `src_endpoint.uid`, `src_endpoint.os`, and `status_code`.
- URL Filtering status code and content type become `http_response`, threat categories `finding_info.types`, WildFire email details `evidences[].email`, and certificate fingerprints `tls.certificate.fingerprints`.
- Mapped records keep their log type and subtype in `unmapped`.

*By @zedoraps.*

### Palo Alto Networks syslog receiver for v6

The Palo Alto Networks package now parses PAN-OS CSV payloads with positional input and output fields. It also maps PAN-OS Traffic, URL Filtering, Threat, and supported GlobalProtect authentication records to OCSF 1.9. Other parsed families become OCSF Base Events and retain their structured fields in `unmapped`.

Normalize a Syslog record in one call:

```tql
accept_udp "0.0.0.0:514"
this = data.parse_syslog()
paloalto::ocsf::normalize
```

Use `paloalto::parse` and `paloalto::ocsf::map` separately when a pipeline needs to inspect or enrich the parsed PAN-OS record before mapping.

*By @mavam in #147.*

## 🐞 Bug fixes

### Correct actions, status, and evidence in PAN-OS OCSF events

PAN-OS Traffic, URL Filtering, and Threat events now map actions, status, HTTP details, and threat evidence correctly.

|                                                                        | Before                            | Now                                                                                                                          |
| ---------------------------------------------------------------------- | --------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| `block-url`, `drop-all-packets`, `reset both`, `drop ICMP`, `sinkhole` | No action                         | Denied with Blocked, Dropped, or Reset                                                                                       |
| `block-continue`, `block-override`                                     | No action                         | Denied, Challenge                                                                                                            |
| Unknown action, such as `syncookie-sent`                               | No action                         | Other with the PAN-OS spelling                                                                                               |
| PAN-OS spelling of an action                                           | Dropped                           | `unmapped.action`                                                                                                            |
| Status of blocked sessions and requests                                | Success                           | Failure                                                                                                                      |
| Status of Traffic `start` and allowed URL requests                     | Success                           | Unknown                                                                                                                      |
| HTTP method `get`                                                      | Unknown activity                  | Get, `http_method: "GET"`                                                                                                    |
| X-Forwarded-For                                                        | String                            | List of addresses                                                                                                            |
| PAN-DB categories                                                      | Labels, rejected by `ocsf_derive` | `category_ids`, such as `46` (News/Media); Other with the label when OCSF has no equivalent; risk ratings stay in `unmapped` |
| Protocol `6`                                                           | `protocol_name: 6`                | `protocol_num: 6`, `protocol_name: "tcp"`                                                                                    |
| Filename of file, virus, and WildFire records                          | URL evidence                      | File evidence, with the WildFire SHA-256                                                                                     |
| Finding title and analytic                                             | Filename, subtype, whole column   | Signature name and ID                                                                                                        |
| WildFire `benign` verdict                                              | Alert                             | Not an alert                                                                                                                 |
| NAT `0.0.0.0`, empty user, rule, or URL, location from a country name  | Empty objects                     | Omitted; the value stays in `unmapped`                                                                                       |
| GlobalProtect `0.0.0.0` for a missing client address                   | Kept as an address                | Omitted                                                                                                                      |

*By @zedoraps.*

### Exact PAN-OS column values and layout variants

`paloalto::parse` keeps PAN-OS columns exactly as written and places them correctly in more layouts; `paloalto::ocsf::normalize` also reads RFC 5424 Syslog.

```
1,2026/05/29 11:00:01,000700000042,TRAFFIC,end,,2026/05/29 11:00:00,192.0.2.70,198.51.100.70,,,00123,…,{link-a, tag-a, ethernet1/1, 2026/05/29 10:59:58, 0, 0, N/A},…
```

- Text columns stay text: rule `00123` and filename `20260529` no longer become integers, and a `;` no longer splits a user agent or change detail into a list.
- `AUTH`, `HIPMATCH`, Tunnel Inspection `START`/`END`, and lowercase `audit` records parse instead of yielding nothing.
- Correlated Events have separate source address and user columns, so severity and evidence are no longer shifted.
- Config records without change details, SD-WAN link switches with commas, and the 125-column URL Filtering layout of PAN-OS 10.1 and later keep every column in place.
- Records with the documented column counts of PAN-OS 8.1, 9.1, and 10.0, such as 65 Traffic or 75 Threat columns, no longer warn; other short records still do. Extra columns land in `excess_values`.
- Times with offsets, such as `2026-05-29T11:00:00.250+02:00`, parse with exact milliseconds; the Unix epoch placeholder of a missing high-resolution timestamp becomes null.
- An RFC 3164 Syslog timestamp no longer becomes the event time; Syslog timestamps stay in `unmapped.timestamp`.

*By @zedoraps.*
