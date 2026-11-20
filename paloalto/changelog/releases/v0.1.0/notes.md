The Palo Alto Networks package now keeps PAN-OS columns exactly as the firewall writes them, recognizes the layouts of more PAN-OS versions and log types, and interprets times in the firewall's time zone. Its OCSF mappings normalize actions, outcomes, files, URLs, and identities consistently, and they map Authentication, GlobalProtect, Config, Data Filtering, Decryption, and Correlated Events records to OCSF classes instead of Base Event.

## 🚀 Features

### OCSF classes for PAN-OS authentication, configuration, DLP, decryption, correlation, and tunnel records

`paloalto::ocsf::map` and `paloalto::ocsf::normalize` now map six more kinds of PAN-OS records to OCSF classes instead of Base Event.

**PAN-OS writes** (Authentication, Config, and GlobalProtect, abbreviated):

```
1,2026/05/29 19:00:01,000700000042,AUTHENTICATION,login,,2026/05/29 19:00:00,vsys1,192.0.2.140,example\dave,…,auth-fail,2,7802,…,RADIUS,…
1,2026/05/29 21:00:01,000700000042,CONFIG,0,,2026/05/29 21:00:00,192.0.2.160,vsys1,delete,admin-example,Web,Failed, vsys vsys1 rulebase security rules example-allow-web,…
1,2026/05/29 20:00:01,000700000042,GLOBALPROTECT,globalprotect,,2026/05/29 20:00:00,vsys1,gateway-connected,tunnel,…,192.0.2.151,…
```

**OCSF before → now:**

| PAN-OS records                                                               | Before                               | Now                                                                                                                                                                                     |
| ---------------------------------------------------------------------------- | ------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Authentication (`AUTHENTICATION`, `AUTH`)                                    | Base Event                           | Authentication (3002): user, source, service, policy, protocol, result, `is_mfa` for additional factors                                                                                 |
| GlobalProtect `portal-auth`, `gateway-auth`                                  | Authentication for any `stage=login` | Authentication only for these event IDs, with IPv6 client fallback                                                                                                                      |
| GlobalProtect `gateway-connected`, `gateway-switch-to-ssl`, `gateway-logout` | Base Event                           | Tunnel Activity (4014): Open, Other, Close, with the tunnel address and login duration                                                                                                  |
| Config                                                                       | Base Event                           | Entity Management (3004): command as activity, configuration path as entity, change details before and after, administrator as actor; a commit's entity is the firewall's configuration |
| Data Filtering (`THREAT` `data`, `dlp`, `dlp-non-file`)                      | Base Event                           | Data Security Finding (2006): data pattern, DLP gateway, file, user, action                                                                                                             |
| Decryption                                                                   | Base Event                           | Network Activity (4001) with TLS version, SNI, server certificate, decryption policy; failure on handshake error                                                                        |
| Correlated Events                                                            | Base Event with shifted fields       | Detection Finding (2004): correlation object as analytic, evidence as description                                                                                                       |

GlobalProtect prelogin, configuration, and host information records, as well as System, User-ID, HIP Match, IP-Tag, Tunnel Inspection, SCTP, and GTP records, stay Base Events with their parsed fields.

**What you need to do:** Queries on `class_uid == 0` for these records now need their class, for example:

```tql
where class_uid == 3004 and actor.user.name == "admin-example"
```

**Why:** Each of these PAN-OS logs describes an activity with an OCSF class. A record without a value that the class requires, such as an Authentication timeout without user, keeps the class and leaves the value missing.

*By @zedoraps.*

### Time zone of PAN-OS times

`paloalto::parse` and `paloalto::ocsf::normalize` now take an optional `timezone` argument for PAN-OS times without a zone, and use the offset of the high-resolution timestamp when you don't set it.

**PAN-OS writes** (System, abbreviated):

```
1,2026/07/15 10:00:01,000700000042,SYSTEM,general,,2026/07/15 10:00:00,…,2026-07-15T10:00:01.250+02:00
```

**OCSF before → now:**

|                                                 | Before                 | Now                                                     |
| ----------------------------------------------- | ---------------------- | ------------------------------------------------------- |
| `time` of `2026/07/15 10:00:00`                 | `2026-07-15T10:00:00Z` | `2026-07-15T08:00:00Z`, from the offset `+02:00`        |
| With `timezone="Europe/Berlin"`                 | Not available          | `2026-07-15T08:00:00Z` in summer, `09:00:00Z` in winter |
| Without `timezone` or high-resolution timestamp | UTC                    | UTC                                                     |

**What you need to do:** Set the firewall's time zone when its records lack a high-resolution timestamp:

```tql
paloalto::ocsf::normalize timezone="Europe/Berlin"
```

An IANA name accounts for daylight saving time, while a fixed offset such as `+01:00` applies to every record.

**Why:** PAN-OS writes most times in the firewall's time zone without naming it, but writes the high-resolution timestamp with its UTC offset.

*By @zedoraps.*

## 🔧 Changes

### Expanded OCSF 1.9 field coverage

PAN-OS OCSF events now expose sequence numbers, traffic and URL-filter endpoint locations and users, and session-end reasons. Country names become location descriptions, while country codes remain ISO-style codes. Conflicting location aliases and vendor-specific context remain in `unmapped`.

*By @mavam in #191.*

### Firewall, record, user, and endpoint context in PAN-OS OCSF events

PAN-OS OCSF events now name the firewall that logged them and carry a record UID and the management-plane receipt time, the User-ID source user becomes the actor, and more endpoint, HTTP response, and Threat context leaves `unmapped`.

**PAN-OS writes** (Traffic, abbreviated):

```
1,2026/05/29 17:00:01,000700000042,TRAFFIC,end,,2026/05/29 17:00:00,192.0.2.130,198.51.100.130,,,allow-web,example\carol,…,60,…,7701,…,tcp-fin,…,fw-example-1,…
```

**OCSF before → now:**

|                                                            | Before                                     | Now                                                                                       |
| ---------------------------------------------------------- | ------------------------------------------ | ----------------------------------------------------------------------------------------- |
| `metadata.reporter`                                        | Not set; `unmapped.device_name`            | `hostname: "fw-example-1"`, `uid: "000700000042"`                                         |
| `metadata.uid`                                             | Not set                                    | `000700000042:TRAFFIC:7701`                                                               |
| `finding_info.uid`                                         | Signature ID or bare sequence number       | `metadata.uid`                                                                            |
| `metadata.logged_time`                                     | Receive time                               | High-resolution timestamp, such as `2026-05-29T17:00:01.250+02:00`, else the receive time |
| `duration`                                                 | Not set; `unmapped.elapsed_time`           | `60000`                                                                                   |
| Device-ID OS and category, VM UUID                         | `unmapped`                                 | `src_endpoint.os`, `type_id`, `instance_uid`, and the same for `dst_endpoint`             |
| URL Filtering HTTP status code and content type            | `unmapped`                                 | `http_response.code`, `content_type`                                                      |
| Threat category, WildFire email sender, recipient, subject | `unmapped`                                 | `finding_info.types`, `evidences[].email`                                                 |
| GlobalProtect host ID, client OS, error code               | `unmapped`                                 | `src_endpoint.uid`, `src_endpoint.os`, `status_code`                                      |
| Decryption certificate fingerprint                         | `unmapped`                                 | `tls.certificate.fingerprints`                                                            |
| Source user                                                | `src_endpoint.owner.name: "example\carol"` | `actor.user`: `name: "carol"`, `domain: "example"`                                        |
| Destination user                                           | `dst_endpoint.owner.name: "example\svc"`   | `dst_endpoint.owner`: `name: "svc"`, `domain: "example"`                                  |
| GlobalProtect portal or gateway                            | `dst_endpoint.hostname`                    | `dst_endpoint.name`                                                                       |
| `type`, `threat_content_type` of mapped records            | Dropped                                    | `unmapped`                                                                                |

**What you need to do:** Update queries on the source user and the GlobalProtect gateway:

```tql
where actor.user.name == "carol" and actor.user.domain == "example"
where dst_endpoint.name == "example-external-gw"
```

**Why:** The device name is the hostname of the logging firewall, the high-resolution timestamp is when its management plane received the record, and PAN-OS numbers records per firewall and log type, so only all three identify a record. PAN-OS defines the source user as the user who initiated the session and writes users as `domain\user`. GlobalProtect portal and gateway columns hold configuration names, not hostnames.

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

PAN-OS Traffic, URL Filtering, and Threat events now map every documented action, report a status that matches the outcome, recognize lowercase HTTP methods, separate files from URLs, and leave out objects that the record doesn't identify.

**PAN-OS writes** (URL Filtering and Threat, abbreviated):

```
…,THREAT,url,…,tcp,block-url,coins.example.test/,(9999),cryptocurrency,…,"unknown, 203.0.113.8",…,propfind,…,"cryptocurrency,medium-risk",…
…,THREAT,virus,…,tcp,reset-both,20260529.exe,Example Virus Signature(400001),any,medium,server-to-client,7601,…
```

**OCSF before → now:**

|                                                                                              | Before                                  | Now                                                                                                                                                                                                    |
| -------------------------------------------------------------------------------------------- | --------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `action_id`, `disposition_id` for `block-url`, `drop-all-packets`, `reset both`, `drop ICMP` | Not set                                 | `2` (Denied) with Blocked, Dropped, or Reset                                                                                                                                                           |
| `block-continue`, `block-override`                                                           | Not set                                 | `2` (Denied), Challenge                                                                                                                                                                                |
| `sinkhole`                                                                                   | Not set                                 | `2` (Denied), Blocked                                                                                                                                                                                  |
| Unknown action, such as `syncookie-sent`                                                     | Not set                                 | `99` (Other) with the PAN-OS spelling                                                                                                                                                                  |
| PAN-OS spelling of a mapped action                                                           | Dropped                                 | `unmapped.action`                                                                                                                                                                                      |
| `status_id` of denied, dropped, reset, or blocked sessions and requests                      | `1` (Success)                           | `2` (Failure)                                                                                                                                                                                          |
| `status_id` of Traffic `start` and allowed URL requests                                      | `1` (Success)                           | `0` (Unknown)                                                                                                                                                                                          |
| `activity_id` for method `get`                                                               | `0` (Unknown)                           | `3` (Get); `http_method: "GET"`                                                                                                                                                                        |
| `http_request.x_forwarded_for`                                                               | String                                  | List of addresses; original text in `unmapped` if it has other tokens                                                                                                                                  |
| `http_request.url.categories`                                                                | PAN-DB label, rejected by `ocsf_derive` | `category_ids` such as `46` (News/Media), `[23, 24]` (Alcohol, Tobacco) for `alcohol-and-tobacco`; `99` (Other) with the label for categories without OCSF equivalent; risk ratings stay in `unmapped` |
| `connection_info` for protocol `6`                                                           | `protocol_name: 6`                      | `protocol_num: 6`, `protocol_name: "tcp"`                                                                                                                                                              |
| Filename of file, virus, and WildFire records                                                | `evidences[].url.url_string`            | `evidences[].file.name`, with the WildFire SHA-256                                                                                                                                                     |
| `finding_info.title`, `analytic.name`                                                        | Filename and subtype                    | Signature name, such as `Example Virus Signature`                                                                                                                                                      |
| `finding_info.analytic.uid`                                                                  | Whole column                            | Signature ID, such as `400001`                                                                                                                                                                         |
| `is_alert` of a WildFire `benign` verdict                                                    | `true`                                  | `false`                                                                                                                                                                                                |
| NAT `0.0.0.0` and port 0, empty user, rule, URL                                              | Empty objects (warnings)                | Omitted                                                                                                                                                                                                |
| `location` from a country name or address range                                              | `desc` only (warning)                   | Omitted; value stays in `unmapped`                                                                                                                                                                     |

**What you need to do:** Queries that count successful denied sessions or match PAN-DB labels in `categories` need an update. For example, replace `http_request.url.categories == ["news"]` with:

```tql
where 46 in http_request.url.category_ids
```

**Why:** PAN-OS names actions per log type and several map to the same OCSF disposition, writes HTTP methods in lowercase, and uses one URL/Filename column for both. The firewall's action says what it enforced, so a blocked session can't have succeeded, while an allowed URL request has no recorded response. OCSF requires typed addresses, category IDs, and identities for every object it contains.

*By @zedoraps.*

### Exact PAN-OS column values and layout variants

`paloalto::parse` now keeps text columns as PAN-OS writes them, reads the `AUTH`, `HIPMATCH`, Tunnel Inspection `START`/`END`, and lowercase `audit` records that it used to reject, and keeps the columns of Correlated Events, Config, URL Filtering, and SD-WAN Traffic records in their documented positions.

**PAN-OS writes** (Traffic, with a rule name `00123` and SD-WAN link switches, abbreviated):

```
1,2026/05/29 11:00:01,000700000042,TRAFFIC,end,,2026/05/29 11:00:00,192.0.2.70,198.51.100.70,,,00123,…,{link-a, tag-a, ethernet1/1, 2026/05/29 10:59:58, 0, 0, N/A},…,general-internet,…,2026-05-29T11:00:00.250+02:00,…
```

**OCSF before → now:**

|                                                                                              | Before                                                | Now                                                |
| -------------------------------------------------------------------------------------------- | ----------------------------------------------------- | -------------------------------------------------- |
| Rule name `00123`, filename `20260529`                                                       | Integer `123`, `20260529` (cast drops them)           | `"00123"`, `"20260529"`                            |
| User agent or change detail with `;`                                                         | List of fragments                                     | One string                                         |
| `AUTH`, `HIPMATCH`, `START`, `END`, `audit` records                                          | Not parsed, Base Event without fields                 | Parsed; `AUTH` and `audit` also mapped             |
| Correlated Events severity and evidence                                                      | Shifted by one column; evidence dropped               | `high`, evidence text                              |
| Config record without change details                                                         | Sequence number in `before_change_detail`             | `sequence_number`                                  |
| Traffic tail after SD-WAN link switches                                                      | Shifted by up to 8 columns                            | Documented positions                               |
| URL Filtering records of PAN-OS 10.1 and later (125 columns)                                 | Shifted by two columns after the request headers      | Documented positions, including `http_status_code` |
| Records with the documented columns of PAN-OS 9.1 or 10.0, such as 75 or 105 Traffic columns | Warning for every record                              | No warning; other short records keep it            |
| Values beyond the documented columns                                                         | Dropped with a warning                                | `excess_values`                                    |
| Times such as `2026-05-29T11:00:00.250+02:00`                                                | Null in GlobalProtect records; `.250` as `.249999999` | Parsed with offset and exact milliseconds          |
| High-resolution time `1969-12-31T16:00:00-08:00`                                             | Unix epoch                                            | Null                                               |
| Syslog timestamp `May 29 11:00:05`                                                           | Event time, null after `ocsf_cast`                    | Only `unmapped.timestamp`                          |

**Why:** PAN-OS writes every column as text, so guessing types turned identifiers into numbers and times. It writes SD-WAN link switches as an unquoted list with commas, Config records without change details have two columns fewer, and PAN-OS 10.1 added two URL Filtering columns in the middle of the record. Older PAN-OS versions write a documented prefix of the current columns. An RFC 3164 timestamp has neither year nor zone, so it can't be an event time.

*By @zedoraps.*
