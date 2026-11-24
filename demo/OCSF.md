# OCSF workload generator

Generate synthetic OCSF 1.9 events with Tenzir. The `demo::ocsf` operators of
the `demo` package emit events that you can pass to any destination. Unlike
the package's feeds, which replay recorded data, these events are synthetic.
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
Copies of the same process within an event share the identifier. Identifiers
are fresh for each generated observation; events do not reconstruct a process
lifetime. Filenames, paths, URLs, hashes, messages, and raw records use the
same final values.

By default, 35% of events are OCSF Base Events (class 0) from 50 source profiles
that have no specific class mapping. Their native fields stay under `unmapped`.

## Run the generator

The package requires Tenzir 6.23 or newer. Install it, or run the pipelines
from a checkout of the Library with `--package-dirs=.`.

Generate a continuous stream at 1,000 events per second:

```tql
demo::ocsf::generate_load eps=1000
```

Generate exactly one million events and finish:

```tql
demo::ocsf::generate count=1000000
```

Generate a historical interval with a daily office-hours pattern:

```tql
demo::ocsf::generate_historical eps_office_hours=1000, eps_off=100,
  start=now() - 30d, days=30
```

The runnable [`ocsf-finite.tql`](examples/ocsf-finite.tql) example writes a finite
dataset as NDJSON. The operators live in the `demo::ocsf` namespace.

## Configure a workload

The following controls apply to the OCSF 1.9 generators. For a smaller
OCSF 1.6 workload, see [Generate legacy events](#generate-legacy-events).

`generate` and `generate_load` accept these options:

| Option | Default | Behavior |
| --- | --- | --- |
| `eps` | `1000` for `generate_load`; unlimited for `generate` | Upper rate in events per second. Must be positive. |
| `class_uid` | Mixed classes | Generate only the selected class when set. Use `0` for base events. |
| `base_event_share` | `0.35` | Fraction of mixed events that are base events. Write a float between `0.0` and `1.0`. |
| `raw` | `"native"` | `"native"` adds `raw_data` only for sources with a native log format. `"json"`, `"kv"`, `"syslog"`, or `"mixed"` add a generic record to every event; `"none"` omits `raw_data`. See [Preserve a source message](#preserve-a-source-message). |
| `raw_message` | `false` | Copy `raw_data`, when present, to an additional `raw_message` field. |
| `observables_probability` | `1.0` | Fraction of events with scalar observables. `0.0` omits them; `1.0` covers every event. |
| `drift_probability` | `0.0` | Fraction of events whose integer `severity_id` becomes a numeric string. |
| `unknown_probability` | `0.0` | Fraction of events with one unknown top-level `unknown_field_<n>` record. |
| `vendor_probability` | `0.0` | Fraction of events with a synthetic top-level `acme` vendor record. |

`demo::ocsf::generate` also accepts `count`, which defaults to `1000000` and must be
nonnegative, and `time_eps`, which defaults to `1000` and sets the logical event
rate for timestamps. A count of zero emits no events. You can combine a finite
count with an output EPS limit:

```tql
demo::ocsf::generate count=10000, eps=1000, class_uid=3002, raw="syslog"
```

`eps` limits how fast events leave the generator. `time_eps` controls how much
event time the finite dataset covers, independently of execution speed:

```tql
demo::ocsf::generate count=1000000, time_eps=1000
```

This dataset spans approximately 16 minutes and 40 seconds. Generation ends
when the events are ready; it does not wait for that event-time interval.

The continuous operator generates five seconds' worth of events every five
seconds and limits its output in one-second windows. It emits batches, so
`eps=1000` does not promise one event every millisecond. When a round takes
longer than five seconds to generate, the achieved rate falls below `eps`. A
slower downstream destination applies backpressure and reduces the achieved
rate. Stop a continuous stream with the caller's cancellation mechanism or an
operator such as `head`.

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
demo::ocsf::generate count=1000000000, needle_ip_count=1,
  needle_dns_count=10, needle_command_count=1000
```

Counts refer to matching **events in the target field**, not string occurrences
across the complete JSON document. A value can also appear in the event's raw
message, descriptive message, or observables. The generator reserves distinct
event positions for each kind, overrides their classes, and leaves the remaining
class mix unchanged. Needle positions span the logical timeline with gaps that
differ by at most one event. Kinds occupy consecutive bands of those positions;
class batching emits them in no guaranteed order. The counts must be
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
demo::ocsf::generate count=1000000, drift_probability=0.001,
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

`demo::ocsf::generate_historical` covers the half-open interval `[start, start + days)`.
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
and source records remain consistent. Class batching can
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
demo::ocsf::generate_historical eps_office_hours=2, eps_off=1,
  start=2026-10-01, days=1, raw="none"
```

This produces 118,800 events. The runnable
[`ocsf-historical.tql`](examples/ocsf-historical.tql) example writes a historical
dataset to NDJSON.

## Inspect the event mix

Each class has its own operator under `operators/classes/`. The package covers
Base Event and 45 OCSF 1.9.0 classes. It leaves out the classes that OCSF 1.9
deprecates and classes for which the package has no source to model, such as
kernel, memory, registry, and unmanned-system events.

The default mix favors routine traffic and successful operations, and assumes
`base_event_share=0.35`.

| Class UID | Class | Share | Scenarios |
| --- | --- | --- | --- |
| 0 | Base Event | 35.00% | 50 unclassified source profiles; see below |
| 1001 | File System Activity | 2.53% | Read, create, update, delete |
| 1005 | Module Activity | 0.63% | Load, unload, invoke; SSL and crypto libraries |
| 1006 | Scheduled Job Activity | 0.63% | Start, create, update, disable |
| 1007 | Process Activity | 3.38% | Launch, successful exit, nonzero exit, open handle |
| 1008 | Event Log Activity | 0.63% | Rotate, export, archive, clear |
| 1009 | Script Activity | 0.63% | Reporting, inventory, deployment, backup |
| 2002 | Vulnerability Finding | 0.63% | TLS, SSH, web package assessments and remediation |
| 2003 | Compliance Finding | 0.63% | Pass, warning, fail, resolved exposure |
| 2004 | Detection Finding | 0.84% | Authentication, process, network, API anomaly |
| 2005 | Incident Finding | 0.63% | New, in progress, on hold, closed |
| 2006 | Data Security Finding | 0.63% | Personal data, financial data, credentials, resolved exposure |
| 3002 | Authentication | 5.06% | SSH logon, failure, logout; OIDC success and failure |
| 3003 | Authorize Session | 0.63% | Assign groups, privileges, roles; denied assignment |
| 3004 | Entity Management | 0.63% | Read, create, update, failed disable |
| 3006 | Group Management | 0.63% | Add/remove user, assign/revoke privilege |
| 3007 | User Management | 0.63% | Password change/reset, enable, failed disable |
| 3008 | Role Management | 0.63% | Assign/remove privileges, attach/detach policy |
| 4001 | Network Activity | 10.13% | Traffic summary, open, refused, reset |
| 4002 | HTTP Activity | 8.44% | GET 200, POST 201, GET 404, GET 503 |
| 4003 | DNS Activity | 8.44% | A, AAAA, NXDOMAIN, query only |
| 4004 | DHCP Activity | 0.63% | ACK, renewal request, release, NAK |
| 4005 | RDP Activity | 0.63% | Connect response, traffic, disconnect, failed connect |
| 4006 | SMB Activity | 0.63% | Open, create, overwrite, denied open |
| 4007 | SSH Activity | 0.63% | Traffic, open, close, fail |
| 4008 | FTP Activity | 0.63% | Get, put, list, denied get |
| 4009 | Email Activity | 1.69% | Internal send, inbound receive, scan, outbound send |
| 4013 | NTP Activity | 0.63% | Client/server exchanges, delay and synchronization states |
| 4014 | Tunnel Activity | 0.63% | Open, renew, close, failed open |
| 5001 | Device Inventory Info | 0.63% | Collected and logged OS inventory variants |
| 5003 | User Inventory Info | 0.63% | Logged/collected users, administrator, disabled account |
| 5004 | Operating System Patch State | 0.63% | Four observed OS patch versions |
| 5019 | Device Config State Change | 0.63% | Enabled protection, disabled protection or SELinux |
| 5020 | Software Inventory Info | 0.63% | Firefox, OpenSSH, Python, Git |
| 5023 | Cloud Resources Inventory Info | 0.63% | Two S3 buckets and two IAM roles |
| 6001 | Web Resources Activity | 0.63% | Read, create, update, denied share |
| 6002 | Application Lifecycle | 0.63% | Start, restart, update, failed stop |
| 6003 | API Activity | 1.69% | List, create, delete, access denied |
| 6005 | Datastore Activity | 0.63% | Query, write, update, denied query |
| 6006 | File Hosting Activity | 0.63% | Download, upload, share, denied delete |
| 6007 | Scan Activity | 0.63% | Complete, start, cancel, error |
| 6008 | Application Error | 0.63% | Timeout, refused connection, invalid response, unavailable upstream |
| 7001 | Remediation Activity | 0.63% | Isolate, evict, restore, failed harden |
| 7002 | File Remediation Activity | 0.63% | Evict, restore, isolate, failed eviction |
| 7003 | Process Remediation Activity | 0.63% | Evict, isolate, detect, failed eviction |
| 7004 | Network Remediation Activity | 0.63% | Isolate, evict, restore, failed harden |

These percentages are sampling probabilities. Small samples may omit rare
classes. Use `class_uid` to select one class, or `base_event_share=0.0` to
generate only mapped classes in the same relative proportions. Not every
optional attribute or nested path is populated.

Nine classes model sources with a native log format: file, process, and
authentication events, detection findings, network, HTTP, DNS, and email
activity, and API calls. `metadata.product` names a real product only where
the package renders that product's own log format: Windows Security, Sysmon,
PowerShell, Zeek, Suricata, PAN-OS, FortiGate, nginx, Apache HTTP Server,
OpenSSH, AWS CloudTrail, and AWS Security Hub. The other classes
use generic product names, such as "Identity provider" or "Mail server", cover
four scenarios each, and have no `raw_data` by default. One class can have several sources: a connection comes from a
sensor, a firewall, or Sysmon, each with its own share. See
[Preserve a source message](#preserve-a-source-message) for the shares.
`metadata.source` marks the workload as synthetic, and `metadata.loggers`
identifies the generator.

The events are synthetic. They are schema-valid and internally consistent, but
they do not reproduce every field that a real mapping of the same source
writes, and they are no substitute for captured logs.

Optional values vary by event, including hostnames, email addresses, user
agents, referrers, file sizes, traffic counters, and detection confidence.
Some scenarios omit whole objects, such as answers for DNS queries and NXDOMAIN
responses. Required class fields remain present.

## Generate base events

Many sources never get a specific OCSF mapping. The generator emits them
as OCSF 1.9 Base Events: `class_uid`, `category_uid`, and `type_uid` are `0`, or
`type_uid` is `99` when `activity_id` is `99` (Other) and the source names its
own `activity_name`. `severity_id` is always present, but about half of these
events carry `0` (Unknown) and most others `1` (Informational). Sources with a
native level map it, sometimes as `99` with the original `severity` string.
`status_id` appears only when the source reports an outcome.

The profiles are invented. Except for the Windows Application log, which is
rendered as Windows event XML, they carry generic product names and field
layouts of the package's own design, which resemble common kinds of products
without following any vendor's format.

Each event comes from one of 50 source profiles in five groups:

| Group | Profiles |
| --- | --- |
| Applications | Order service, container platform, edge API, billing worker, Windows Application log, cron scripts, mobile telemetry, Java runtime GC log, search slow log, feature flag audit |
| Infrastructure | Load balancer, router, hypervisor, application delivery controller, in-memory cache, switch, storage system, backup server, workload scheduler, UPS |
| SaaS | Source code hosting, team chat, issue tracker, CRM, video conferencing, help desk, on-call paging, HR system, payment service, e-signature service |
| Appliances and IoT | Email gateway, wireless controller, print management, badge readers, MQTT environment sensors, video management, building management, meeting room devices, canteen point of sale, fire alarm panel |
| Operations and legacy | CI server, CI runner, message broker, automation controller, GitOps controller, infrastructure-as-code service, relational database audit, ERP audit, mainframe records, midrange audit journal |

Profile frequencies form a long tail. The most common profile produces about 4%
of base events; the rarest produces about 0.04%. Each profile sets its own
`metadata.product`, `log_name`, and `log_provider`, a recurring set of
`unmapped` keys, nesting depth, and value types, and one-line messages. Events of one profile therefore share a shape, while different
products differ. Values reuse the organization's users, workstations, and
services, so names, hosts, and addresses match the mapped classes. Shared
appliances use fixed hosts in `10.30.0.0/24`; printers, switches, access points,
and room systems use the sampled user's division domain.

Some profiles drift types on a stable key, for example meeting IDs, mainframe
return codes, switch VLANs, CSV-derived CRM numbers, and sensor readings.
About 20% of base events also receive ad-hoc keys: a `debug` record, one of 40
numbered `custom_field_<n>` keys that is a string or an integer, an `_ingest`
record, or numbered tags.

Mapping choices are stable per profile, as they would be for one parser. Two
thirds of the profiles keep the reporting `device` and declare the `host`
profile; together they produce about 68% of base events. Observables are
extracted separately using `observables_probability`. Every base event has
`metadata.logged_time`, and 40% of the profiles keep
`metadata.original_time` in their native clock format. Base events do not
receive the related objects described below. Apart from the Windows
Application log, they have no `raw_data` by default. A generic raw record, when
requested, names the reporting device as `host`, the user only when the source
reports one, and the `unmapped` fields as `extra`.

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
| `host` | Endpoint, inventory, and authentication events, and Sysmon network and DNS events | Device identity and the initiating user. Authentication identifies the bastion, domain controller, or identity-provider server as the observing device. Network sensors, firewalls, and web servers report neither. |
| `cloud` | Selected API calls, connections to the cloud API service, and cloud API findings | AWS provider, recurring account, region, and a matching availability zone. |
| `security_control` | Selected file, process, network, login, API, and detection events | Policy, action, disposition, and alert flag. Access failures are unauthorized; passive observations are logged; findings can raise alerts. |
| `ai_operation` | Selected API calls, HTTP requests, process launches, and file reads | One of three recurring internal assistants, its model and run identity, and optional tool-call context with consistent token totals. |
| `incident` | Incident findings | Finding list and incident lifecycle state. |
| `container` | Selected Linux process events | Container identity, image digest, and namespace PID. |
| `data_classification` | Selected file events | Business data category, confidentiality, and classification status. |
| `datetime` | Selected network events | `time_dt` matching the native event timestamp. |
| `load_balancer` | Selected HTTP events | Balancer identity, IP, destination, and response code. |
| `network_proxy` | Selected HTTP events | Proxy endpoint and matching connection, request, and response. |
| `osint` | Selected detection findings | IP intelligence with confidence, vendor, and TLP. |
| `record_integrity` | Selected event-log operations | SHA-256 fingerprint of the final event, excluding its fingerprint. |
| `trace` | Selected API calls | Trace and span identities, operation, service, and consistent timestamps. |
| `linux/linux_users` | Linux process events | Effective user/group IDs, audit user ID, and process group. |
| `macos/macos_users` | macOS process events | Effective user and group IDs. |

The recurring workstations are 80% Windows, 15% Linux, and 5% macOS. Linux and
macOS process events declare their corresponding extension, `linux` (UID `1`)
or `macos` (UID `3`), alongside the OS profile.

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

- DNS wire flags, authority records, and additional records; HTTP cookies;
  SMTP envelope addresses and authentication results.
- Network observation points and initiator roles; RDP capabilities, keyboard,
  and display; SMB dialects and share identity; FTP data ports and responses;
  NTP dispersion.
- File results, process launch types and access masks, and previous security
  states.
- Analyst notes, incident impact assessments, and scan counters that reconcile
  with the file totals.

Fields appear only on applicable classes and scenarios; individual events
contain a subset. Native messages preserve the fields supported by their
source format.

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
| Vulnerability assessment | Remediation for the referenced CVE IDs. The CVE IDs are real, so the events carry no invented scores or package versions. |
| Findings | `attack` adds technique context. ATT&CK mappings include their `tactic` and `technique` objects. |
| AI authority | `delegation` identifies the recurring authority under which an assistant acts. |

OIDC attempts independently replace 12% of logon attempts. These use a generic
identity provider, its endpoint, and the OpenID protocol instead of SSH. Failed
attempts have no issued token. Both SSH and OIDC sessions use native timestamps.
The events remain independently sampled and do not reconstruct a session lifecycle.

Groups follow the assigned user's department. Server groups stay fixed in the
Operations department. Fingerprints and certificate identities are deterministic
for recurring fixtures and hostnames. The generator emits synthetic metadata;
it does not create certificate bodies, signed PDF content, or OIDC token payloads.

Collector context in `unmapped` includes an unsigned sequence and a native
duration. OCSF duration attributes remain integer milliseconds as required by
the schema.

## Generate event times

Events use native Tenzir `time` values, including DNS query and response times.
`generate` and `generate_load` round to millisecond precision. Historical
generation retains finer precision for jitter within each event slot.
`generate` captures one anchor at invocation time minus 10 seconds, then
computes each timestamp as
`anchor - count / time_eps seconds + index / time_eps seconds + jitter`.
Each index covers a distinct position in the timeline.
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

OCSF calls the original message field `raw_data`. For sources with a native
log format, the generator renders a source message from the same user, host,
time, and event values as the normalized event, and records its format in
`metadata.log_format`. Other sources have neither field unless you request a
generic format. It reads the
final event fields after optional values have been omitted. Values are shared
with the normalized event, rather than independently randomized.

### Native formats

By default (`raw="native"`), sources with a renderer write their native log
format, so `raw_data` has the layout that a collector receives from that
product. The format
follows the product and log type:

| `metadata.log_format` | Format | Sources and classes |
| --- | --- | --- |
| `windows-xml` | Windows event XML with `System`, `EventData`, and `RenderingInfo` | Windows Security 4624/4625/4634 (3002), 4688/4689/4656 (1007), and 4663 (1001); Sysmon 1/5/10 (1007), 3 (4001), 11/23 (1001), and 22 (4003); PowerShell 4104 script blocks (1009); the Windows Application log base profile |
| `zeek-tsv` | Zeek tab-separated logs | `conn.log` (4001), `http.log` (4002), `dns.log` (4003), `dhcp.log` (4004), `rdp.log` (4005), `smb_files.log` (4006), `ftp.log` (4008), `ntp.log` (4013) |
| `eve-json` | Suricata EVE JSON | `flow` (4001), `http` (4002), `dns` (4003), `alert` (2004) |
| `pan-os-csv` | PAN-OS syslog CSV | `TRAFFIC` (4001); `THREAT` with subtype `url` (4002) and `spyware` (2004) |
| `combined` | Combined access log | nginx and Apache HTTP Server (4002) |
| `fortigate-kv` | FortiGate key=value | `traffic`/`forward` (4001) |
| `syslog-rfc3164` | BSD syslog | OpenSSH `sshd` on the bastion host (3002, 4007) |
| `cloudtrail-json` | CloudTrail record | S3 data events (6003) |
| `asff-json` | EventBridge event with an ASFF finding | Security Hub and Inspector findings (2002, 2003) |
| `nginx-error` | nginx file error log | nginx application errors (6008) |

Classes with several sources split them as follows. Shares are sampling
probabilities; sources that exist only on Windows apply to the four in five
Windows workstations, and the other events fall back to the network sensor or
a generic endpoint agent.

| Class | Sources |
| --- | --- |
| 1001 File system activity | Linux and macOS: generic endpoint agent. Windows: generic endpoint agent 25%, Sysmon 45% for creation and deletion, Security log 30% plus the reads and writes that Sysmon does not report |
| 1007 Process activity | Linux and macOS: generic endpoint agent. Windows: generic endpoint agent 30%, Sysmon 40%, Security log 30% |
| 1009 Script activity | Linux: generic endpoint agent. Windows: PowerShell script block logging |
| 2004 Detection finding | Network anomalies: Suricata 60%, PAN-OS 40%. Others: generic endpoint agent |
| 3002 Authentication | A generic identity provider for 12% of logon attempts; Windows Security for 80% of the remaining attempts from Windows workstations; OpenSSH for the rest |
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
  session ID. Sysmon `ProcessGuid` values are `process.uid`.
- Windows logons record the account SID in `user.uid_alt`. Process events record
  MD5 and SHA-256 hashes of the binary in `process.file.hashes`.
- CloudTrail `eventID` is `metadata.uid`, and `requestID` is `api.request.uid`
  when present. Security Hub findings use `finding_info.uid`.
- Sources report additional native details, such as logon GUIDs, firewall rule
  names, TLS metadata, and sensor configuration, which have no OCSF field here.

Each format escapes its values: XML text uses entities and encodes line breaks
as character references, PAN-OS quotes free-form CSV fields and doubles
embedded quotes, access logs write embedded quotes as `\x22`, and JSON formats
use the JSON printer. Every record is a single line.

Record sizes depend on the source. Compact network and access logs are smaller
than endpoint XML and finding envelopes. PowerShell script blocks reuse eight
functions written for this package and can contain an embedded base64 blob,
producing a long tail. These are synthetic source records, not captures from
real devices, and they carry only the fields the generator fills.

Zeek and Suricata HTTP records describe the clear-text backend leg behind the
TLS proxy: HTTP/1.1, port 80, and an `http` URL. Web server access logs and PAN-OS
URL filtering retain the HTTPS connection. Optional TLS objects are only added
to connections on port 443.

### Generic formats

`raw="json"`, `raw="kv"`, and `raw="syslog"` render every event in one generic
format, including events whose source has a native format. `raw="mixed"` picks
one of the three at random for each event. The record is of the generator's
own design, not a product's format. It describes the event in words and
carries no OCSF IDs.

- JSON contains a timestamp, host, user, event ID, source product, outcome,
  message, class-specific fields, and source extras.
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

The organization is computed, not stored. [`constants.tql`](constants.tql)
holds the small pools: 100 first and 20 last names, eight services, eight web
pages, six documents, four programs, and six email subjects. Every event
derives its user, workstation, and service from an index, so identities stay
related without large lookup tables: user 21 is always `alice.chen`, owns
`ws-021`, and sits in the second division's subnet.

To change the organization size, edit `$ocsf_division_count`. `$ocsf_division_size` must
stay 20, because every seat of a division combines one first name with one
last name, and the operating-system shares depend on the seat.

`$ocsf_file_probability` and `$ocsf_uri_probability` control the fraction of fresh
filename and URI components. Set either probability to zero to use only the
recurring values for that field.

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
demo::ocsf::generate_legacy count=10000
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
| `raw` | `"none"` | `"json"` adds a generic source record as `raw_data`. |

The legacy operator has a fixed schema version and a smaller interface than
the 1.9 generators. Native vendor log rendering, exact-count needles,
optional schema drift, and historical office-hour patterns are available
through the 1.9 generators. Unsupported legacy options fail compilation;
invalid argument values emit a diagnostic and no events.

To combine both versions with exact counts, merge their streams:

```tql
demo::ocsf::generate count=90000
merge {
  demo::ocsf::generate_legacy count=10000
}
```

This produces exactly 100,000 events, with 10% using OCSF 1.6.0. The stream
order is unspecified. The runnable
[`ocsf-legacy-mixed.tql`](examples/ocsf-legacy-mixed.tql) example writes this dataset
as NDJSON. The existing generators continue to emit only OCSF 1.9.0.

## Choose an output

The generator has no storage dependency. Append `to_file`, `to_kafka`, or
another destination to the pipeline.

NDJSON supports the mixed stream. For Parquet, generate one class per file and
select a stable set of fields. The runnable
[`ocsf-network-parquet.tql`](examples/ocsf-network-parquet.tql) example keeps the
core network fields and source message:

```tql
demo::ocsf::generate count=1000000, class_uid=4001
select metadata.version, metadata.product, metadata.uid, metadata.log_name,
  metadata.log_format, time, category_uid, class_uid, activity_id, type_uid,
  severity_id, status_id, src_endpoint.ip, src_endpoint.port,
  dst_endpoint.ip, dst_endpoint.port, connection_info, message, raw_data
to_file "network-activity.parquet" {
  write_parquet compression_type="zstd"
}
```

Optional field omission changes the record shape even within one class. The
Parquet writer requires a stable schema, so directly writing the
unprojected stream can fail. Parquet schema and destination performance are
separate from generation throughput.

## Test the package

Run from the Library checkout:

```sh
uvx tenzir-test demo/tests/ocsf
```

The TQL tests exercise finite and continuous generation, the default class mix,
all 15 profiles, native timestamps, OCSF casting and derivation, exact needle
counts, and historical interval boundaries. They parse the native formats and
compare their source values with normalized fields. Additional assertions
check process ancestry, file metadata, scan
counters, certificate SANs, and observable identities.
Random UUIDs, timestamps, and complete event records are not snapshot values.
Legacy tests also check all five 1.6 classes, their field layouts, source
messages, class filters, empty output, and a mixed 1.6/1.9 stream.

Events carry these native Tenzir kinds: bool, int, uint, float, time,
duration, string, IP, subnet, list, and record.

To measure generation throughput independently of a destination:

```tql
demo::ocsf::generate count=1000000
discard
```

The generator builds a 32,768-event seed batch, reuses it, and populates the
events batch by batch. Raw rendering and optional context add processing
cost. Generation itself does not call `ocsf_cast`; tests validate the events
separately.
