# OCSF 1.9 unmapped-field audit

## Scope and method

The audit covers the library's OCSF mapping operators, including shared helpers,
class-specific branches, fallback events, and the final construction of
`unmapped`. The starting fixture inventory contained 1,335 distinct residual
field paths across 23 packages. Parser and aggregation tests supplement the OCSF
fixtures; some of their residual fields never reach an OCSF mapping branch.

Use [OCSF 1.9.0](https://schema.ocsf.io/1.9.0/) as the schema reference. A field
needs a semantic match on its actual event class, not just a similar name on an
unrelated object. Check inherited attributes and enabled profiles as well as the
leaf class. Preserve unknown source fields and unsupported fallback payloads.
The inventory is fixture-backed, not an exhaustive list of arbitrary keys that
an open-ended source record might contain.

## Promoted fields

| Package | Source fields | OCSF destination |
| --- | --- | --- |
| abusech / ThreatFox | `id`, `reporter`, `malware_malpedia` | OSINT external ID, creator, and references |
| abusech / MalwareBazaar | `telfhash`, `gimphash` | File fingerprints with `algorithm_id: 99` and the source algorithm name |
| alphaMountain | `sections.first_seen`, `sections.last_seen`; flat `sections.geo.isoCode`, `latLng`, `asn.number`, `asn.organization` | OSINT creation/modification times and unambiguous single-result location/ASN |
| Anthropic / OpenAI | Instrumentation `scope.version` with a scope name | `metadata.loggers[].version`; do not confuse it with the application or schema version |
| Check Point | Web-control `app_name`, `proto`, endpoint fields, `user`, `bytes_in`, `bytes_out`, `category`; network `ifname` | Shared connection/security context, traffic, URL categories, and the third-party observation point |
| Cisco Umbrella | `organization_id` | `metadata.tenant_uid` |
| DHCPD | Caller-provided `hostname` | Host-profile `device.hostname` |
| Fortinet | `devname`, `devid`; web-filter `agent`, `catdesc`; endpoint country names | Device identity, HTTP user agent, URL categories, and location descriptions |
| Microsoft Windows | Kerberos `PreAuthType`, `TicketOptions`, `ServiceName`, `ServiceSid`, complete `CertIssuerName` / `CertSerialNumber` / `CertThumbprint` | Authentication protocol, Kerberos token flags, service identity, and PKINIT certificate; retain the pre-auth mechanism code |
| Microsoft Windows | RDP `LogonID`, `TargetLogonId` | Connection session UID, not an additional user identity |
| Microsoft Windows | Crash/error faulting-module name, path, version; error/hang process-start FILETIME | `module.file` and `process.created_time` |
| Microsoft Windows | Service `ServiceStartType`, `ServiceType`; account `DisplayName`, `UserPrincipalName` | Translated Windows service enums and user names; preserve unknown service combinations as `Other` |
| NetFlow / IPFIX | `ingress_interface`, `egress_interface`, `dot1q_vlan_id`, `post_dot1q_vlan_id` | Source/destination interface and VLAN UIDs |
| Okta | Client `device.id`, `device.name`, `device.osVersion` | Client endpoint, or the finding's evidence endpoint; do not overwrite an existing endpoint UID or consume these on Base Event |
| Palo Alto | `sequence_number`; traffic / URL-filter country/location and user fields; `session_end_reason` | Metadata sequence, endpoint location/owner, and status detail |
| Sophos | Endpoint `osVersion`, a single `macAddresses` value | Device OS version and MAC |
| Splunk CIM | Nonstandard `process_integrity_level` | Integrity caption accompanying `integrity_id: 99` |
| Suricata DNS | `id`, `opcode`, `version`, answer `rrname`, authority/additional records, boolean DNS header flags; legacy scalar question/answer fields | DNS transaction ID, opcode, log version, records/sections, and flag IDs; distinguish request and response additional sections |
| Suricata | TCP header flags on network classes; TLS `notbefore`, `ja4`, `subjectaltname`; SSH implementation strings; file hashes / magic description | Connection flags, certificate creation time/SANs, JA4 list, endpoint agents, and file fingerprints/description |
| Zeek | DNS `trans_id`, `AA`, `TC`, `RD`, `RA`, `AD`, `CD`; HTTP body lengths / username; FTP user; SMTP URLs | DNS transaction/flags, HTTP request/response lengths, host-profile actor, and email URLs |
| Zeek | Connection timestamps, VLAN; SMB access/create/modify times, size, file ID; SSH version and authentication result; network `_system_name` | Traffic interval, VLAN UID, file attributes, SSH protocol/status, and third-party observation point |
| BIND named | Query-log `+` and `C` flags | Recursion Desired and Checking Disabled flag IDs |

A BIND `D` flag is EDNS DNSSEC OK, not Authenticated Data; `K` describes a DNS
COOKIE, not Checking Disabled. Keep the original flag string for EDNS,
signature, and COOKIE information. See the [ISC query-log flag reference](https://kb.isc.org/docs/aa-00434).

## Consumed duplicate aliases

Consume only aliases whose information is represented in the normalized event:

- DNS numeric query type/class alongside their mapped mnemonic in Zeek and
  Umbrella.
- Zeek HTTP `dest_host` when it supplies the mapped host.
- Equal Suricata SSH client/server protocol versions; keep a differing client
  version.
- Sophos endpoint hostname, object type, platform, and a single already-mapped
  IP. Preserve multiple IPs and MACs rather than choosing an arbitrary one.
- DHCPD relay display values matching the mapped typed relay IP/interface.
- Equal Palo Alto country/location aliases. Keep conflicting aliases.

## Retention decisions

These groups cover the remaining fixture-backed source fields. Unknown keys
continue to flow through the existing `unmapped` record.

| Package | Retained fields and rationale |
| --- | --- |
| abusech | Feed lifecycle/status, download/upload counters, anonymity and compromise flags, origin country, classification-tool results, code-signing details, icon-specific hashes, aliases, and feed intelligence. A sample-origin country is not an endpoint location; an icon hash is not a hash of the full sample. |
| alphaMountain | Multi-address geo/ASN results, DNS helper arrays and lookup names, geographic ratings, category source/scope, vendor scores, auxiliary host/URL representations, and request metadata. Do not flatten one address's context onto every indicator or conflate distinct scoring systems. |
| Amazon | `interface_id` and arbitrary test residue. A VPC flow's ENI is not necessarily the source or destination interface without its direction/attachment context. |
| Anthropic | Command/content/tool-parameter hashes, hook identity, permission provenance/trigger, MCP scope/stdio transport, opaque tool parameters, and incomplete span context. Invocation IDs are not independent log-record IDs; log spans do not provide a trace span's required lifetime. |
| Check Point | Proprietary bitmaps and encoded policy tags; rule/layer/match arrays; interface direction outside supported network context; management domain/operation/vendor data; partially populated email/DLP/threat payloads. Do not attach a network observation point to a finding or reinterpret a management domain as a network domain. |
| Cisco | Identity/group strings and identity-type vocabularies, vendor category lists and rule IDs without an unambiguous principal or rule model. Keep unsupported product branches intact. |
| DCSO | Admiralty/decay scores, ignore/state, feed sources and feed-occurrence times, MITRE software references, and targeting countries/industries. Feed occurrence is not necessarily an indicator observation; target markets are not the observed endpoint's location. |
| DHCPD | DHCPv6 IAID and identity-association/prefix details, relay envelopes, lease-found/status text, daemon/parser/template markers, and partial/fallback client/server data. These are not DHCP transaction IDs or a complete lease event; keep relay display values that do not match a mapped relay. |
| Fortinet | Address-object UUIDs (`srcuuid`/`dstuuid`), session/policy/vendor flags, counters, FortiExtender/radio/SIM/carrier metrics, VPN/IPsec details, taxonomy/scores, and unsupported subtype payloads. Address-object UUIDs do not identify endpoint devices. `Reserved` country values describe address classes, not geography. Isolated `certhash` / `scertcname` / `scertissuer` fields do not supply the required certificate issuer and serial together. |
| Microsoft | Windows message-resource tokens and sentinel values; pre-auth method codes; logon/security/account bitmasks; PE timestamps, fault offsets and WER IDs; task/job/provider details; Graph property bags, multi-target changes, conditional-access diagnostics and lifecycle timestamps without matching event semantics. Keep incomplete PKINIT certificates rather than fabricate required issuer/serial fields. |
| MISP | Organization/tag structures not already normalized, tag colour and exportability. Taxonomy display attributes are not generic event classification enums. |
| named | Client memory pointers, views/zones/serials and operational parser context, query flags beyond mapped header bits, and unsupported daemon records. A client object address is not a DNS transaction ID. |
| NetFlow | Exporter/template/observation-domain metadata, uptime/raw timing fallbacks, counters and sampling information, subnet-prefix lengths, IP service/class bytes and vendor information elements. Distinguish exporter scope, endpoint scope, and counter semantics. |
| Okta | Device trust/registration/management/screen-lock/security facts, authentication/provider hints, MFA push provenance, risk-engine and debug data, administrative targets and integrations, and unknown event types. Preserve a device ID that conflicts with the already-mapped client ID. |
| OpenAI | Tool invocation IDs, opaque arguments/hashes, transport and peer details, account/billing/authentication/environment hints, token subtype details, span context without lifetime, and file-size metrics without a measured file. Keep scopes and durations distinct from application and aggregate semantics. |
| OpenSSH | Parser/session-aggregation remnants, authentication attempts and PAM attribution, pre-auth markers, connection/child/session process IDs without supported process objects, certificate/authorized-key paths and textual credentials, syslog facility/structured data, routing domain, and arbitrary caller context. Partially parsed source records are not completed authentication or SSH events. |
| Palo Alto | Vendor bitmaps, device-group hierarchy, content version and threat-specific identifiers, unsupported system/audit payloads, and conflicting location aliases. Country names use location descriptions; country codes use `location.country`. |
| Sophos | Threat/malware taxonomy and endpoint-health/security-state objects, multilayer product telemetry, endpoint IP/MAC lists with multiple values, generic metadata, and opaque entity payloads on fallback events. Do not turn an arbitrary endpoint UUID into a NIC UUID. |
| Splunk | Tags/data-model markers, alias fields, partially normalized process/file/user/network data, unsupported CIM objects, and parallel timing/protocol fields with different semantics. A similarly named attribute on another OCSF class is not a valid destination. |
| Suricata | DNS `tx_id`, raw flags/grouped forms and reserved bits; TCP per-direction flags/state; flow/application/parser/alert diagnostics; protocol-specific nested fields on unsupported classes; TLS/SSH negotiation details, differing protocol versions, and file-transfer state/IDs without identity guarantees. EVE `tx_id` is an application transaction counter, not the DNS header ID. |
| Tenzir | Evidence/content hashes, secret-detector kinds and arbitrary vendor context. Do not represent a content hash as a signed record-integrity attestation. |
| Zeek | Observer name on non-network classes, per-layer byte counts, connection state/history/missed bytes, TLS cipher/signature/negotiation details and SAN/fingerprint residues without full certificate identity, SMB metadata-change time, FTP passwords, SMTP routing/capture details, RDP client settings, and unsupported protocol records. File metadata-change time is not content modification time. |
| Zscaler | Application sanction status, bandwidth throttling, DLP engines/dictionaries, scanned-file taxonomy, key-protection and unscannable types, and proprietary threat class/category values. Do not invent a malware classification or a named file from taxonomy alone. |

## Regression coverage

Existing snapshots cover the promoted fixture fields. New tests exercise PKINIT
certificate completeness, service-type combinations, FILETIME conversion, DNS
record sections/flags and reserved residue, HTTP response-header preservation,
nonstandard fingerprints, flat geo results, logger versions, and country names
versus codes. These tests cast the normalized output with `ocsf_cast` before
checking its destination and residue fields.
