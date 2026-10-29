# OCSF workload generator

Generate synthetic OCSF 1.9 events with Tenzir and Nova. The `ocsf_generate` package emits
events that you can pass to any compatible destination.
The separate `generate_legacy` operator produces OCSF 1.6.0 events for five
common classes.

The default workload models an organization with 2,000 recurring users,
2,000 assigned workstations, 800 service endpoints, and 100 organization
domains. It reuses 800 base URLs, 600 base file names, 400 process/command
fixtures, 600 email subjects, 400 user agents, and 100 partner domains.
A user's ID, name, email, workstation hostname, and IP stay related across
event classes and across runs. The workstation pool is 80% Windows, 15% Linux,
and 5% macOS. Endpoint events use matching paths, processes, and log sources.
UUIDs, timestamps, ephemeral ports, traffic counters, and event choices change
on each occurrence.

The generator also adds fresh UUID components to 25% of regular-file names and
30% of HTTP URLs. Filename suffixes preserve the extension and parent directory.
HTTP variations split between an `/items/<uuid>` path suffix and a
`?request_id=<uuid>&page=<number>` query. Web resource URLs also receive optional
request-ID queries. The remaining values recur from the base pools.

Process objects use random UUIDv4 identifiers, including actors and parents.
CrowdStrike Falcon telemetry instead uses sensor-style 12-digit decimal process
IDs, as in its `TargetProcessId` field. Copies of the same process within an
event share the identifier. Identifiers are
fresh for each generated observation; events do not reconstruct a process lifetime.
Filenames, paths, URLs, hashes, messages, and raw records use the same final values.

By default, 35% of events are OCSF Base Events (class 0) from 50 source profiles
that have no specific class mapping. Their native fields stay under `unmapped`.

## Run the generator

Run these commands from the Library checkout. The package requires Tenzir
6.20 or newer with Nova enabled. The examples allow prereleases explicitly.

Generate a continuous stream at 1,000 events per second:

```sh
uvx --prerelease=allow tenzir --nova --package-dirs=. 'ocsf_generate::generate_load eps=1000'
```

Generate exactly one million events and finish:

```sh
uvx --prerelease=allow tenzir --nova --package-dirs=. 'ocsf_generate::generate count=1000000'
```

Generate a historical interval with a daily office-hours pattern:

```tql
ocsf_generate::generate_historical eps_office_hours=1000, eps_off=100,
  start=now() - 30d, days=30
```

Write a finite dataset as NDJSON:

```sh
uvx --prerelease=allow tenzir --nova --package-dirs=. -f ocsf_generate/examples/finite.tql
```

Set `--package-dirs=/absolute/path/to/library` when running from another
directory. The package ID and TQL namespace are `ocsf_generate`.

## Configure a workload

The following controls apply to the OCSF 1.9 generators. For a smaller
OCSF 1.6 workload, see [Generate legacy events](#generate-legacy-events).

`generate` and `generate_load` accept these options:

| Option | Default | Behavior |
| --- | --- | --- |
| `eps` | `1000` for `generate_load`; unlimited for `generate` | Upper rate in events per second. Must be positive. |
| `class_uid` | Mixed classes | Generate only the selected class when set. Use `0` for base events. |
| `base_event_share` | `0.35` | Fraction of mixed events that are base events. Write a float between `0.0` and `1.0`. |
| `raw` | `"native"` | `"native"`, `"json"`, `"kv"`, `"syslog"`, `"mixed"`, or `"none"`. See [Preserve a source message](#preserve-a-source-message). |
| `raw_message` | `false` | Copy `raw_data` to an additional `raw_message` field. |
| `observables_probability` | `1.0` | Fraction of events with scalar observables. `0.0` omits them; `1.0` covers every event. |
| `drift_probability` | `0.0` | Fraction of events whose integer `severity_id` becomes a numeric string. |
| `unknown_probability` | `0.0` | Fraction of events with one unknown top-level `unknown_field_<n>` record. |
| `vendor_probability` | `0.0` | Fraction of events with a synthetic top-level `acme` vendor record. |

`ocsf_generate::generate` also accepts `count`, which defaults to `1000000` and must be
nonnegative, and `time_eps`, which defaults to `1000` and sets the logical event
rate for timestamps. A count of zero emits no events. You can combine a finite
count with an output EPS limit:

```tql
ocsf_generate::generate count=10000, eps=1000, class_uid=3002, raw="syslog"
```

`eps` limits how fast events leave the generator. `time_eps` controls how much
event time the finite dataset covers, independently of execution speed:

```tql
ocsf_generate::generate count=1000000, time_eps=1000
```

This dataset spans approximately 16 minutes and 40 seconds. Generation ends
when the events are ready; it does not wait for that event-time interval.

The continuous operator starts a bounded round every five seconds, with output
limited in one-second windows. Longer rounds reduce setup overhead. It emits batches,
so `eps=1000` does not promise one event every millisecond. Round setup costs can
reduce the achieved rate for large values of `eps`. A slower downstream
destination applies backpressure and reduces the achieved rate. Stop a
continuous stream with the caller's cancellation mechanism or an operator such
as `head`.

An unsupported class or raw format emits a diagnostic and no events for that
round, following TQL's `assert` behavior.

## Control lookup and IOC selectivity

The finite operators `generate` and `generate_historical` accept three exact
needle counts, each defaulting to zero:

| Option | Reserved value | Target field and class |
| --- | --- | --- |
| `needle_ip_count` | `198.18.0.1` | `dst_endpoint.ip` in Network activity (4001) |
| `needle_dns_count` | `dns-needle.ocsf-gen.invalid` | `query.hostname` in DNS activity (4003) |
| `needle_command_count` | `ocsf-gen-needle --ioc` | `process.cmd_line` in Process activity (1007) |

For example, generate one billion events with three known lookup selectivities:

```tql
ocsf_generate::generate count=1000000000, needle_ip_count=1,
  needle_dns_count=10, needle_command_count=1000
```

Counts refer to matching **events in the target field**, not string occurrences
across the complete JSON document. A value can also appear in the event's raw
message, descriptive message, or observables. The generator reserves distinct
event positions for each kind, overrides their classes, and leaves the remaining
class mix unchanged. Needle positions span the logical timeline with gaps that
differ by at most one event. Kinds occupy consecutive bands of those positions;
concurrent branches emit them in no guaranteed order. The counts must be
nonnegative and their sum cannot exceed the total event count. A class filter
must agree with every enabled needle kind. Full consumption of the finite call
is required; downstream filtering or `head` can remove needle events.

The default fixtures never contain these reserved values. Keep custom fixture
values outside `198.18.0.0/15`, the `.ocsf-gen.invalid` namespace, and the needle
command. Each call has its own counts. Continuous generation has no finite
boundary and does not expose exact needle counts.

## Configure observables and schema irregularities

Every event has one or more `observables` by default, independently of the
5% detailed-object sampling. Observables reference final scalar fields such as
endpoint IPs, DNS names, URLs, user IDs, and file paths. Each entry includes its
source `metadata.uid` as `event_uid`. Events with no mapped entity reference
their actual `message` with type 99 (`Source message`). Set
`observables_probability=0.0` to omit the array, or choose a fraction between
zero and one. Rich mapped events also add synthetic reputation metadata.

To exercise schema drift and catch-all handling, enable the probabilities
independently:

```tql
ocsf_generate::generate count=1000000, drift_probability=0.001,
  unknown_probability=0.001, vendor_probability=0.001
```

Each probability applies independently to each event, so categories can overlap
and finite samples fluctuate around their configured fractions. Type drift
intentionally violates OCSF's integer type for `severity_id`. Unknown fields
vary among eight top-level names. The `acme` record contains a sensor zone,
policy revision, and verdict; it is a synthetic vendor payload for catch-all
tests, not a registered OCSF schema extension. The generator does not declare
it in `metadata.extensions`. Standard OCSF fields remain valid when type drift
is disabled; a strict validator may reject undeclared top-level fields.

Irregularities are applied to normalized fields **after raw-log rendering**.
Raw data preserves the valid source representation, allowing normalization and
casting tests to inspect deliberately malformed output without breaking native
serializers. These controls supplement the existing variations under `unmapped`.

## Generate historical office-hours traffic

`ocsf_generate::generate_historical` covers the half-open interval `[start, start + days)`.
`days` is a nonnegative integer number of 24-hour days. If you omit `start`, it
defaults to invocation time minus `days` days, so the interval ends near now.

Every day, including weekends, has office hours from 08:00 inclusive to 17:00
exclusive in UTC. Each complete office-hour second contains exactly
`eps_office_hours` events. The other seconds contain `eps_off` events. Within
each second, events occupy evenly spaced slots with random jitter inside their
slot. For example, 1,000 events per second use 1 ms slots, while 100 use 10 ms
slots. Partial boundary seconds are clipped to the requested interval.

These rates describe event timestamps and counts. The operator generates the
history as fast as the downstream pipeline permits, then finishes. Timestamps
are assigned before class fields, profiles, and raw messages, so related times
and source records remain consistent. Parallel branches and class batching can
emit events out of timestamp order; the operator does not globally sort them.
Events leave grouped by class, and base events are regrouped by source profile,
so a short prefix of the output does not reflect the class mix.

The daily count is `32400 * eps_office_hours + 54000 * eps_off`, even when the
interval starts partway through a day. Both rates must be nonnegative, and at
least one must be positive. Set `eps_off=0` to omit off-hours events. The operator
also accepts `class_uid`, `base_event_share`, raw-format options, observable and
irregularity probabilities, and exact needle counts with the same behavior as
`generate`.

The 30-day example at 1,000/100 EPS generates 1,134,000,000 events. For a smaller
trial, use lower logical rates:

```tql
ocsf_generate::generate_historical eps_office_hours=2, eps_off=1,
  start=2026-10-01, days=1, raw="none"
```

This produces 118,800 events. The runnable
[`historical.tql`](examples/historical.tql) example writes a historical
dataset to NDJSON.

## Inspect the event mix

Each class has its own UDO under `operators/classes/`. The package covers
all 79 concrete core classes and all seven Windows extension classes in OCSF
1.9.0, plus Base Event: 87 event types in total. This includes deprecated classes
for compatibility and the two unmanned-system classes. Category headings and
abstract parent classes are excluded.

The default mix favors routine traffic and successful operations. The shares
assume `base_event_share=0.35`. The 41 added classes each receive one sampling
slot; existing classes retain their relative weights in the other 308 slots.

| Class UID | Class | Share | Scenarios |
| --- | --- | --- | --- |
| 0 | Base Event | 35.00% | 50 unclassified source profiles; see below |
| 1001 | File System Activity | 2.23% | Read, create, update, delete |
| 1002 | Kernel Extension Activity | 0.19% | Load and unload an OS-specific kernel extension |
| 1003 | Kernel Activity | 0.19% | Kernel object operations |
| 1004 | Memory Activity | 0.19% | Memory allocation, access, protection, and injection |
| 1005 | Module Activity | 0.56% | Load, unload, invoke; SSL and crypto libraries |
| 1006 | Scheduled Job Activity | 0.56% | Start, create, update, disable |
| 1007 | Process Activity | 2.98% | Launch, successful exit, nonzero exit, open handle |
| 1008 | Event Log Activity | 0.56% | Rotate, export, archive, clear |
| 1009 | Script Activity | 0.56% | Reporting, inventory, deployment, backup |
| 1010 | Peripheral Activity | 0.19% | Peripheral attachment, removal, enable, and disable |
| 1011 | Device Power State Activity | 0.19% | Boot, shutdown, sleep, and wake |
| 1012 | Clipboard Activity | 0.19% | Clipboard operations with typed text items |
| 2001 | Security Finding | 0.19% | Legacy findings and investigation states |
| 2002 | Vulnerability Finding | 0.56% | TLS, SSH, web package assessments and remediation |
| 2003 | Compliance Finding | 0.56% | Pass, warning, fail, resolved exposure |
| 2004 | Detection Finding | 0.74% | Authentication, process, network, API anomaly |
| 2005 | Incident Finding | 0.56% | New, in progress, on hold, closed |
| 2006 | Data Security Finding | 0.56% | Personal data, financial data, credentials, resolved exposure |
| 2007 | Application Security Posture Finding | 0.19% | Dependency, policy, exposure, and resolved posture findings |
| 2008 | IAM Analysis Finding | 0.19% | Privilege, dormant account, cross-account, and resolved findings |
| 3001 | Account Change | 0.19% | Legacy account operations |
| 3002 | Authentication | 4.47% | SSH logon, failure, logout; OIDC success and failure |
| 3003 | Authorize Session | 0.56% | Assign groups, privileges, roles; denied assignment |
| 3004 | Entity Management | 0.56% | Read, create, update, failed disable |
| 3005 | User Access Management | 0.19% | User access and privilege operations |
| 3006 | Group Management | 0.56% | Add/remove user, assign/revoke privilege |
| 3007 | User Management | 0.56% | Password change/reset, enable, failed disable |
| 3008 | Role Management | 0.56% | Assign/remove privileges, attach/detach policy |
| 4001 | Network Activity | 8.94% | Traffic summary, open, refused, reset |
| 4002 | HTTP Activity | 7.45% | GET 200, POST 201, GET 404, GET 503 |
| 4003 | DNS Activity | 7.45% | A, AAAA, NXDOMAIN, query only |
| 4004 | DHCP Activity | 0.56% | ACK, renewal request, release, NAK |
| 4005 | RDP Activity | 0.56% | Connect response, traffic, disconnect, failed connect |
| 4006 | SMB Activity | 0.56% | Open, create, overwrite, denied open |
| 4007 | SSH Activity | 0.56% | Traffic, open, close, fail |
| 4008 | FTP Activity | 0.56% | Get, put, list, denied get |
| 4009 | Email Activity | 1.49% | Internal send, inbound receive, scan, outbound send |
| 4010 | Network File Activity | 0.19% | Network file operations |
| 4011 | Email File Activity | 0.19% | Email attachment operations |
| 4012 | Email URL Activity | 0.19% | Email URL operations |
| 4013 | NTP Activity | 0.56% | Client/server exchanges, delay and synchronization states |
| 4014 | Tunnel Activity | 0.56% | Open, renew, close, failed open |
| 5001 | Device Inventory Info | 0.56% | Collected and logged OS inventory variants |
| 5002 | Device Config State | 0.19% | Encryption, firewall, screen-lock, and drift observations |
| 5003 | User Inventory Info | 0.56% | Logged/collected users, administrator, disabled account |
| 5004 | Operating System Patch State | 0.56% | Four observed OS patch versions |
| 5006 | Kernel Object Query | 0.19% | Collected, not found, not applicable, and error query outcomes |
| 5007 | File Query | 0.19% | Collected, not found, not applicable, and error query outcomes |
| 5008 | Folder Query | 0.19% | Collected, not found, not applicable, and error query outcomes |
| 5009 | Admin Group Query | 0.19% | Collected, not found, not applicable, and error query outcomes |
| 5010 | Job Query | 0.19% | Collected, not found, not applicable, and error query outcomes |
| 5011 | Module Query | 0.19% | Collected, not found, not applicable, and error query outcomes |
| 5012 | Network Connection Query | 0.19% | Collected, not found, not applicable, and error query outcomes |
| 5013 | Networks Query | 0.19% | Collected, not found, not applicable, and error query outcomes |
| 5014 | Peripheral Device Query | 0.19% | Collected, not found, not applicable, and error query outcomes |
| 5015 | Process Query | 0.19% | Collected, not found, not applicable, and error query outcomes |
| 5016 | Service Query | 0.19% | Collected, not found, not applicable, and error query outcomes |
| 5017 | User Session Query | 0.19% | Collected, not found, not applicable, and error query outcomes |
| 5018 | User Query | 0.19% | Collected, not found, not applicable, and error query outcomes |
| 5019 | Device Config State Change | 0.56% | Enabled protection, disabled protection or SELinux |
| 5020 | Software Inventory Info | 0.56% | Firefox, OpenSSH, Python, Git |
| 5021 | OSINT Inventory Info | 0.19% | IP intelligence with confidence and TLP |
| 5022 | Startup Item Query | 0.19% | Collected, not found, not applicable, and error query outcomes |
| 5023 | Cloud Resources Inventory Info | 0.56% | Two S3 buckets and two IAM roles |
| 5040 | Live Evidence Info | 0.19% | Live user evidence and query outcomes |
| 6001 | Web Resources Activity | 0.56% | Read, create, update, denied share |
| 6002 | Application Lifecycle | 0.56% | Start, restart, update, failed stop |
| 6003 | API Activity | 1.49% | List, create, delete, access denied |
| 6004 | Web Resource Access Activity | 0.19% | Web resource access outcomes |
| 6005 | Datastore Activity | 0.56% | Query, write, update, denied query |
| 6006 | File Hosting Activity | 0.56% | Download, upload, share, denied delete |
| 6007 | Scan Activity | 0.56% | Complete, start, cancel, error |
| 6008 | Application Error | 0.56% | Timeout, refused connection, invalid response, unavailable upstream |
| 7001 | Remediation Activity | 0.56% | Isolate, evict, restore, failed harden |
| 7002 | File Remediation Activity | 0.56% | Evict, restore, isolate, failed eviction |
| 7003 | Process Remediation Activity | 0.56% | Evict, isolate, detect, failed eviction |
| 7004 | Network Remediation Activity | 0.56% | Isolate, evict, restore, failed harden |
| 8001 | Drone Flights Activity | 0.19% | Drone flight telemetry |
| 8002 | Airborne Broadcast Activity | 0.19% | Remote ID broadcasts |
| 201001 | Registry Key Activity | 0.19% | Registry key operations |
| 201002 | Registry Value Activity | 0.19% | Registry value operations |
| 201003 | Windows Resource Activity | 0.19% | Access to named Windows resources |
| 201004 | Windows Service Activity | 0.19% | Windows service operations |
| 205004 | Registry Key Query | 0.19% | Collected, not found, not applicable, and error query outcomes |
| 205005 | Registry Value Query | 0.19% | Collected, not found, not applicable, and error query outcomes |
| 205019 | Prefetch Query | 0.19% | Collected, not found, not applicable, and error query outcomes |

These percentages are sampling probabilities. Small samples may omit rare
classes. Use `class_uid` to select one class, or `base_event_share=0.0` to
generate only concrete classes in the same relative proportions. Full class
coverage describes supported event types; it does not imply that every
optional attribute or nested path is populated.

The original endpoint and network fields follow shapes used by the local Tenzir
Library's Zeek, OpenSSH, Amazon VPC Flow, and Sysmon mappings. `metadata.product`
identifies an example source appropriate to the class and scenario, for example
Windows Security, Sysmon, PowerShell, CrowdStrike Falcon, Zeek, Suricata, PAN-OS,
FortiGate, nginx, Apache HTTP Server, OpenSSH, Keycloak, Postfix, AWS CloudTrail,
osquery, Security Hub, Purview, ServiceNow, Nextcloud, PostgreSQL, OpenVPN, or
systemd. One class can have several sources: a connection comes from a sensor,
a firewall, or Sysmon, each with its own share. See
[Preserve a source message](#preserve-a-source-message) for the shares.
`metadata.source` marks the workload as synthetic, and `metadata.loggers`
identifies the generator.

Optional values vary by event, including hostnames, email addresses, user
agents, referrers, file sizes, traffic counters, and detection confidence.
Some scenarios omit whole objects, such as answers for DNS queries and NXDOMAIN
responses. Required class fields remain present.

## Generate base events

Many real sources never get a specific OCSF mapping. The generator emits them
as OCSF 1.9 Base Events: `class_uid`, `category_uid`, and `type_uid` are `0`, or
`type_uid` is `99` when `activity_id` is `99` (Other) and the source names its
own `activity_name`. `severity_id` is always present, but about half of these
events carry `0` (Unknown) and most others `1` (Informational). Sources with a
native level map it, sometimes as `99` with the original `severity` string.
`status_id` appears only when the source reports an outcome.

Each event comes from one of 50 source profiles in five groups:

| Group | Profiles |
| --- | --- |
| Applications | Order service (logback), Kubernetes container logs, Node.js API (pino), billing worker (structlog), Windows Application log, cron scripts, mobile telemetry, JVM GC log, OpenSearch slow log, LaunchDarkly audit |
| Infrastructure | HAProxy, Cisco IOS XE syslog, VMware ESXi, F5 BIG-IP LTM, Redis, Aruba AOS-CX, NetApp ONTAP, Veeam, Nomad, APC UPS |
| SaaS | GitHub, Slack, Jira, Salesforce Event Monitoring, Zoom, Zendesk, PagerDuty, Workday, Stripe, DocuSign |
| Appliances and IoT | Cisco Secure Email Gateway, UniFi Wi-Fi, PaperCut printers, LenelS2 badge readers, MQTT environment sensors, Axis cameras, Siemens building management, Cisco RoomOS, canteen point of sale, Honeywell fire panel |
| Operations and legacy | Jenkins, GitLab Runner, RabbitMQ, Ansible, Argo CD, HCP Terraform, Oracle unified audit, SAP security audit, IBM z/OS SMF, IBM i audit journal |

Profile frequencies form a long tail. The most common profile produces about 4%
of base events; the rarest produces about 0.04%. Each profile sets its own
`metadata.product`, `log_name`, and `log_provider`, a recurring set of
`unmapped` keys, nesting depth, and value types, and realistic one-line
messages. Events of one profile therefore share a shape, while different
products differ. Values reuse the organization's users, workstations, and
services, so names, hosts, and addresses match the mapped classes. Shared
appliances use fixed hosts in `10.30.0.0/24`; printers, switches, access points,
and room systems use the sampled user's division domain.

Some profiles drift types on a stable key, for example Zoom meeting IDs, z/OS
return codes, switch VLANs, CSV-derived Salesforce numbers, and sensor readings.
About 20% of base events also receive ad-hoc keys: a `debug` record, one of 40
numbered `custom_field_<n>` keys that is a string or an integer, an `_ingest`
record, or numbered tags. A 200,000-event sample contains about 490 distinct
`unmapped` key paths.

Mapping choices are stable per profile, as they would be for one parser. Two
thirds of the profiles keep the reporting `device` and declare the `host`
profile; together they produce about 68% of base events. Observables are
extracted separately using `observables_probability`. Every base event has
`metadata.logged_time`, and 40% of the profiles keep
`metadata.original_time` in their native clock format. Base events do not
receive the related objects described below. Their raw record names the
reporting device as `host`, the user only when the source reports one, and the
`unmapped` fields as `extra`.

## Add profile context

The generator covers all 13 core profiles and both OS extension profiles in
OCSF 1.9.0. Incident findings declare `incident`, and cloud resource inventories
always include cloud context. Each selected profile is declared in
`metadata.profiles` and populates its corresponding event fields. Native raw
formats retain the context their source format supports. Events can combine
profiles, while others omit the profile list.
Each profile is applied only to classes that support it and to relevant scenarios.

| Profile | Generated scenarios | Context |
| --- | --- | --- |
| `host` | Endpoint, query, inventory, authentication, and selected network observations | Device identity and the initiating user. Authentication identifies the bastion or identity-provider server as the observing device. |
| `cloud` | Selected API calls, connections to the cloud API service, and cloud API findings | AWS provider, recurring account, region, and a matching availability zone. |
| `security_control` | Selected file, process, network, login, API, and detection events | Policy, action, disposition, and alert flag. Access failures are unauthorized; passive observations are logged; findings can raise alerts. |
| `ai_operation` | Selected API calls, HTTP requests, process launches, and file reads | One of three recurring internal assistants, its model and run identity, and optional tool-call context with consistent token totals. |
| `incident` | Incident findings | Finding list and incident lifecycle state. |
| `container` | Selected Linux process events | Container identity, image digest, tag, and namespace PID. |
| `data_classification` | Selected file events | Business data category, confidentiality, and classification status. |
| `datetime` | Selected network events | `time_dt` matching the native event timestamp. |
| `load_balancer` | Selected HTTP events | Balancer identity, IP, destination, and response code. |
| `network_proxy` | Selected HTTP events | Proxy endpoint and matching connection, request, and response. |
| `osint` | Selected detection findings | IP intelligence with confidence, vendor, and TLP. |
| `record_integrity` | Selected event-log operations | SHA-256 fingerprint of the final event, excluding its fingerprint. |
| `trace` | Selected API calls | Trace and span identities, operation, service, and consistent timestamps. |
| `linux/linux_users` | Linux process events | Effective user/group IDs, audit user ID, and process group. |
| `macos/macos_users` | macOS process events | Effective user and group IDs. |

The recurring workstations are 80% Windows, 15% Linux, and 5% macOS. Windows
extension classes select Windows workstations and declare extension `win` (UID
`2`). Linux and macOS process events declare their corresponding extension,
`linux` (UID `1`) or `macos` (UID `3`), alongside the OS profile.

Record integrity uses compact NDJSON in emitted field order, without a trailing
newline. The hash covers the complete final event, including the attestation's
identity, with its fingerprint omitted. `fingerprint.serialization_id=99`
names this representation. These are unsigned integrity checks; editing or
casting an event changes its fingerprint input. Deliberate drift is applied
after fingerprinting and therefore invalidates the fingerprint.

For agent-mediated operations, model identity appears in `ai_agent.ai_model`.
The model and agent names represent an example internal deployment. Passive
observations do not claim to block an operation, and normal application errors
do not automatically become security alerts. Profile context is additive and
preserves the existing event identities, outcomes, and logical timestamps.

## Populate optional fields

Selected protocol and endpoint classes add optional context to half of their
sampled observations. These fields are separate from the 5% detailed
object enrichment:

- DNS wire flags, authority records, and additional records; HTTP cookies and
  status; SMTP envelope addresses and authentication results.
- Network observation points and initiator roles; RDP capabilities, keyboard,
  and display; SMB dialects and share identity; FTP data ports and responses;
  NTP dispersion.
- File results, process launch types and access masks, registry and service
  state before changes, prefetch history, software packages, and assessments.
- Analyst notes, incident impact assessments, and scan counters that reconcile
  with the file totals.

A large sample targets at least 60% of the 325 top-level fields declared across
all concrete OCSF 1.9 classes with profiles and extensions. Base Event is
excluded from this width calculation. Fields appear only on applicable classes
and scenarios; individual events contain a subset. Native messages preserve
the fields supported by their source format.

## Add related objects

The generator samples detailed context for 5% of mapped events and populates related
objects where they apply. Other events retain their smaller shape. Shared
builders preserve user, file, and process identities across related contexts.
The added object types cover these relationships:

| Context | Objects and behavior |
| --- | --- |
| Host | `os`, `agent`, `network_interface`, and `location` describe the assigned operating system, endpoint sensor, interface, and office. Device identity and metadata recur consistently. |
| Identity | `group`, `organization`, `iam_role`, `authorization`, and `session` describe departments, AWS roles, access decisions, and sampled login sessions. Authorization agrees with the event outcome and policy. |
| Federation | `idp` and `authentication_token` describe optional OIDC authentication against Acme Identity. Token metadata appears only after successful authentication. |
| HTTPS | `tls`, `certificate`, `fingerprint`, and `http_header` describe successful TLS traffic and HTTP exchanges. Certificate subjects match SNI; Host and request-ID headers match the request. |
| Files | `fingerprint` and `digital_signature` describe recurring fixture files and signed PDF metadata. Signature digests match the file fingerprint. |
| Process | Creation and termination times, ancestry, command lines, environment variables, sessions, and Windows integrity levels. Parent identities agree with the actor and ancestry. |
| Endpoint detail | Hardware serials and UUIDs, OS builds, MAC addresses, and native device subnets. |
| Resource ownership | Owners and criticality on resource references; account lock and MFA state on users; role policy references. |
| Application detail | HTTP response latency, forwarded addresses, API responses, trace parent IDs, and container runtime, orchestrator, and pod UUIDs. |
| Vulnerability assessment | CVSS 3.1 vector and score, affected package versions, fix versions, and remediation. These are explicitly labeled synthetic benchmark assessments, rather than authoritative advisory metadata. |
| Findings | `attack` adds technique context. ATT&CK mappings include their `tactic` and `technique` objects. |
| AI authority | `delegation` identifies the recurring authority under which an assistant acts. |

OIDC attempts independently replace 12% of logon attempts. These use Keycloak,
the identity-provider endpoint, and the OpenID protocol instead of SSH. Failed
attempts have no issued token. Both SSH and OIDC sessions use native timestamps.
The events remain independently sampled and do not reconstruct a session lifecycle.

Groups follow the assigned user's department. Server groups stay fixed in the
Operations department. Fingerprints and certificate identities are deterministic
for recurring fixtures and hostnames. The generator emits synthetic metadata;
it does not create certificate bodies, signed PDF content, or OIDC token payloads.

Binary clipboard examples also retain the equivalent text representation.
OCSF logical byte strings export as Base64; their native Tenzir representation
is `blob`. Collector context in `unmapped` includes an unsigned sequence, a
native duration, and a null value. OCSF duration attributes remain integer
milliseconds as required by the schema.

Detailed raw records include a `context` record with matching source values,
such as the sensor ID, OS version, session ID, TLS peer, file hash, technique ID,
and delegation ID. This preserves source values without duplicating the entire
normalized event. JSON retains the context record; KV and syslog flatten it.
Native formats include only the context values their product reports.
Change `$object_probability` in `constants.tql` to adjust the fraction of
detailed records. Increasing it increases the payload size and processing cost.

## Generate event times

Events use native Tenzir `time` values, including DNS query and response times.
`generate` and `generate_load` round to millisecond precision. Historical
generation retains finer precision for jitter within each event slot.
`generate` captures one anchor at invocation time minus 10 seconds, then
computes each timestamp as
`anchor - count / time_eps seconds + index / time_eps seconds + jitter`.
Each index covers a distinct position in the timeline across the four branches.
Jitter is sampled independently within ±5 milliseconds, then timestamps are
rounded down to milliseconds. The last events fall near the anchor.

Continuous generation uses a random lookback between 10 and 130 seconds from
the current wall clock. Arrival order does not imply event-time order in either
mode. Raw JSON and key/value messages encode their timestamps as integer
milliseconds since the Unix epoch.

These are independent events drawn from a shared organization. They do not
simulate a stateful incident, reconstruct process lifetimes, or pair every
login with a later logout. Event generation is nondeterministic: repeated calls
with identical arguments, including a fixed historical start, produce different
UUIDs, sampled entities, timestamps, and event choices. There is no numeric seed
option. Fixture expansion is deterministic, and the configured needle event
counts are exact, but neither guarantees repeatable event content or ordering.

## Preserve a source message

OCSF calls the original message field `raw_data`. The generator renders a
source message from the same user, host, time, and event values as the
normalized event, and records its format in `metadata.log_format`. It reads the
final event fields after optional values have been omitted. Values are shared
with the normalized event, rather than independently randomized.

### Native formats

By default (`raw="native"`), sources with a supported renderer write their native log format, so
`raw_data` resembles what a collector receives from that product. The format
follows the product and log type:

| `metadata.log_format` | Format | Sources and classes |
| --- | --- | --- |
| `windows-xml` | Windows event XML with `System`, `EventData`, and `RenderingInfo` | Windows Security 4624/4625/4634 (3002), 4688/4689/4656 (1007), and 4663 (1001); Sysmon 1/5/10 (1007), 3 (4001), 11/23 (1001), and 22 (4003); PowerShell 4104 script blocks (1009); the Windows Application log base profile |
| `zeek-tsv` | Zeek tab-separated logs | `conn.log` (4001), `http.log` (4002), `dns.log` (4003), `dhcp.log` (4004), `rdp.log` (4005), `smb_files.log` (4006), `ftp.log` (4008), `ntp.log` (4013) |
| `falcon-json` | CrowdStrike Falcon JSON | Flat FDR events with about 50 to 90 keys for processes, file creations/writes/deletions, and module loads; Event Streams detection summaries (2004) and response audit events (7001-7004) |
| `eve-json` | Suricata EVE JSON | `flow` (4001), `http` (4002), `dns` (4003), `alert` (2004) |
| `pan-os-csv` | PAN-OS syslog CSV | `TRAFFIC` (4001); `THREAT` with subtype `url` (4002) and `spyware` (2004) |
| `combined` | Combined access log | nginx and Apache HTTP Server (4002) |
| `fortigate-kv` | FortiGate key=value | `traffic`/`forward` (4001) |
| `syslog-rfc3164` | BSD syslog | OpenSSH `sshd` on the bastion host (3002, 4007) |
| `cloudtrail-json` | CloudTrail record | S3 data events (6003) |
| `asff-json` | EventBridge event with an ASFF finding | Security Hub and Inspector findings (2002, 2003) |
| `json` | Generic JSON, described below | Keycloak, Nextcloud, osquery, AWS Config, Purview, ServiceNow; Falcon observations without a supported native event family; base event profiles of the application and SaaS groups |
| `syslog` | Generic RFC 5424 syslog | Postfix, systemd, OpenVPN, PostgreSQL; infrastructure and appliance base profiles |
| `kv` | Generic key/value | Operations and legacy base profiles |
| `nginx-error` | nginx file error log | nginx application errors (6008) |

Classes with several sources split them as follows. Shares are sampling
probabilities; sources that exist only on Windows apply to the four in five
Windows workstations, and the other events fall back to the network sensor or
the cross-platform agent.

| Class | Sources |
| --- | --- |
| 1001 File system activity | Linux: Falcon. Windows: Falcon 25%, Sysmon 45% for creation and deletion, Security log 30% plus the reads and writes that Sysmon does not report |
| 1007 Process activity | Linux: Falcon. Windows: Falcon 30%, Sysmon 40%, Security log 30% |
| 1009 Script activity | Linux: Falcon. Windows: PowerShell script block logging |
| 2004 Detection finding | Network anomalies: Suricata 60%, PAN-OS 40%. Others: Falcon |
| 3002 Authentication | Keycloak for 12% of logon attempts; Windows Security for 80% of the remaining attempts from Windows workstations; OpenSSH for the rest |
| 4001 Network activity | PAN-OS 25%, FortiGate 25%, Suricata 10%, Zeek 10%, Sysmon 30% of Windows connection attempts; Zeek also takes the attempts that Sysmon does not report |
| 4002 HTTP activity | nginx 30%, Apache 15%, PAN-OS URL filtering 15%, Suricata 15%, Zeek 25% |
| 4003 DNS activity | Sysmon 50% of answered Windows lookups, Suricata 20%, Zeek for the rest |

Native records are consistent with the normalized event, so a parser can
recover the mapped fields:

- Times, hosts, users, addresses, ports, URLs, query names, answers, file
  paths, command lines, hashes, and outcomes appear in the source's own
  notation, for example epoch seconds in Zeek, `SystemTime` in Windows XML, and
  `22/Oct/2026:09:17:55 +0000` in access logs.
- `connection_info.uid` holds the Zeek UID, Suricata flow ID, or firewall
  session ID. Sysmon `ProcessGuid` values are `process.uid`, and Falcon
  `TargetProcessId` and `ContextProcessId` values are the process UIDs.
- Windows logons record the account SID in `user.uid_alt`. Process events record
  MD5 and SHA-256 hashes of the binary in `process.file.hashes`.
- CloudTrail `eventID` is `metadata.uid`, and `requestID` is `api.request.uid`
  when present. Security Hub and Falcon detections use `finding_info.uid`.
- Sources report additional native details, such as logon GUIDs, firewall rule
  names, TLS metadata, and sensor configuration, which have no OCSF field here.

Each format escapes its values: XML text uses entities and encodes line breaks
as character references, PAN-OS quotes free-form CSV fields and doubles
embedded quotes, access logs write embedded quotes as `\x22`, and JSON formats
use the JSON printer. Every record is a single line.

Record sizes depend on the source. Compact network and access logs are smaller
than endpoint XML and finding envelopes. PowerShell script blocks reuse function
blocks and can contain an embedded base64 payload, producing a long tail.
These are synthetic source records, not captures from real devices.

Falcon FDR output uses known event families: `ProcessRollup2`, `EndOfProcess`,
`ProcessHandleOpDetectInfo`, `GenericFileWritten`, `FileDeleteInfo`, and
`ClassifiedModuleLoad`. Scheduled jobs, event-log activity, Linux scripts,
scans, module unload/query observations, and file reads use generic JSON rather
than invented FDR event names. Event-family references include the
[CrowdStrike integration's deletion query](https://library.humio.com/integrations/integrations-crowdstrike-fltr-core-crowdstrike-fltr-core.html)
and the [CrowdStrike source event list](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/crowdstrike-source-setup.html).

Zeek and Suricata HTTP records describe the clear-text backend leg behind the
TLS proxy: HTTP/1.1, port 80, and an `http` URL. Web server access logs and PAN-OS
URL filtering retain the HTTPS connection. Optional TLS objects are only added
to connections on port 443.

### Generic formats

`raw="json"`, `raw="kv"`, and `raw="syslog"` render every event in one generic
format. `raw="mixed"` picks one of the three at random for each event, as
earlier versions did by default. Native mode uses the same records for the
sources listed above.

- JSON contains a timestamp, host, user, event ID, source product, activity,
  outcome, message, class-specific fields, and source extras.
- Key/value text contains the same information, with nested fields flattened.
- Syslog uses an RFC 5424-style header with the key/value payload.

Class-specific fields include source and destination addresses and ports, HTTP
methods and status codes, URLs, DNS questions and answers, authentication
methods, process IDs and executable paths, file paths, email recipients, API
operations, and finding titles. Native serializers escape values and support
lists and nested records.

`raw_message=true` adds a convenience alias, which is not a standard OCSF
attribute. Use `raw="none"` to omit the source message.

The `unmapped` object of mapped classes preserves simulated source-specific
extras. Its fields vary in presence and type:

- `observed_host` contains the assigned workstation's native IP or hostname string.
- `retry_count` contains an integer or numeric string when present.
- `collector_zone` samples a small set of location strings.
- `cache_hit`, `source_tags`, and `policy` add booleans, lists, and nested records.

Generic raw records preserve these same values under `extra`; native formats
carry only the fields their product logs. JSON represents IP values
as strings; the normalized event retains their native Tenzir type. Keep the
record form of `unmapped` when checking these type differences. The option
`ocsf_cast encode_variants=true` encodes free-form records as JSON strings.

## Customize the organization

The recurring fixture pools live in [`constants.tql`](constants.tql). Users,
workstations, and services use aligned columns so Nova can sample scalar values
efficiently. Sampling bounds follow the pool lengths. Each HTTP fixture keeps
its hostname and address together, including when several URLs share a host.

To change the organization size, edit the fixture constants. Keep the user and
workstation columns aligned, preserve the corresponding service and HTTP
fixtures, and divide the user pool equally among the four department groups.
Larger constants increase package size and startup cost.

`$randomization.file_probability` and `$randomization.uri_probability` control
the fraction of fresh filename and URI components. Set either probability to
zero to use only the recurring pool for that field.

## Generate legacy events

Use `generate_legacy` to produce a finite OCSF **1.6.0** dataset. It has
dedicated builders for five classes:

| Class | `class_uid` |
| --- | --- |
| File System Activity | `1001` |
| Process Activity | `1007` |
| Authentication | `3002` |
| Network Activity | `4001` |
| DNS Activity | `4003` |

```tql
ocsf_generate::generate_legacy count=10000
```

The operator reuses the organization user, workstation, and service fixtures.
It samples the five classes with equal probability, or generates one class
when you set `class_uid`. Each event has the Host profile and observables.
It generates file creations, process launches, successful and failed logons,
internal TCP connections, and DNS responses.

These events use the 1.6 field layout: `actor.app_name` and `actor.app_uid`,
singular `file.signature` for Windows file creations, and DNS
`query.packet_uid`, `query.opcode_id`, and `answers[].flag_ids`.
The legacy builders omit newer classes, fields, profiles, and extension
declarations. They build 1.6 events directly from fixture values.

| Option | Default | Behavior |
| --- | --- | --- |
| `count` | `1000000` | Exact nonnegative event count. Zero emits no events. |
| `class_uid` | Mixed classes | Select one of the five classes in the table. |
| `eps` | Unlimited | Positive output rate limit in events per second. |
| `time_eps` | `1000` | Positive logical event rate for timestamps. |
| `raw` | `"json"` | Synthetic source JSON, or `"none"` to omit `raw_data`. |

The legacy operator has a fixed schema version and a smaller interface than
the 1.9 generators. Native vendor log rendering, exact-count needles,
optional schema drift, and historical office-hour patterns are available
through the 1.9 generators. Unsupported legacy options fail compilation;
invalid argument values emit a diagnostic and no events.

To combine both versions with exact counts, merge their streams:

```tql
ocsf_generate::generate count=90000
merge {
  ocsf_generate::generate_legacy count=10000
}
```

This produces exactly 100,000 events, with 10% using OCSF 1.6.0. The stream
order is unspecified. The runnable
[`legacy-mixed.tql`](examples/legacy-mixed.tql) example writes this dataset
as NDJSON. The existing generators continue to emit only OCSF 1.9.0.

## Choose an output

The generator has no storage dependency. Append `to_file`, `to_kafka`, or
another destination to the pipeline.

NDJSON supports the mixed stream. For Parquet, generate one class per file and
select a stable set of fields. The runnable
[`network-parquet.tql`](examples/network-parquet.tql) example keeps the
core network fields and source message:

```tql
ocsf_generate::generate count=1000000, class_uid=4001
select metadata.version, metadata.product, metadata.uid, metadata.log_name,
  metadata.log_format, time, category_uid, class_uid, activity_id, type_uid,
  severity_id, status_id, src_endpoint.ip, src_endpoint.port,
  dst_endpoint.ip, dst_endpoint.port, connection_info, message, raw_data
to_file "network-activity.parquet" {
  write_parquet compression_type="zstd"
}
```

Optional field omission changes the record shape even within one class. The
current Nova Parquet writer requires a stable schema, so directly writing the
unprojected stream can fail. Parquet schema and destination performance are
separate from generation throughput.

## Test the package

Run from the Library checkout:

```sh
TENZIR_BINARY="uvx --prerelease=allow tenzir" uvx tenzir-test ocsf_generate --package-dirs=ocsf_generate -j 1
```

The TQL tests exercise finite and continuous generation, all 87 event types,
all 15 profiles, native timestamps, OCSF casting and derivation, exact needle
counts, and historical interval boundaries. They parse the native formats and
compare their source values with normalized fields. Additional assertions
check process ancestry, file metadata, registry and service changes, scan
counters, certificate SANs, package fix versions, and observable identities.
Random UUIDs, timestamps, and complete event records are not snapshot values.
Legacy tests also check all five 1.6 classes, their field layouts, source
messages, class filters, empty output, and a mixed 1.6/1.9 stream.

The generator covers the 24 OCSF logical data types. Nested records and lists
also carry the 13 storable native Tenzir kinds: null, bool, int, uint, float,
time, duration, string, blob, IP, subnet, list, and record. Secrets are runtime
configuration values and cannot appear in generated events. This describes
value kinds, rather than every Arrow storage width or physical encoding.

To measure generation throughput independently of a destination:

```sh
time uvx --prerelease=allow tenzir --nova --package-dirs=. \
  'ocsf_generate::generate count=1000000 | discard'
```

The generator builds a 32,768-event seed batch, reuses it, and populates events
in four concurrent branches. Raw rendering and optional context add processing
cost. These measurements include startup and omit downstream file,
compression, broker, and network costs. Generation itself does not call
`ocsf_cast`; tests validate the events separately.
