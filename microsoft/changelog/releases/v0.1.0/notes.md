The Microsoft package now normalizes Windows Event Log events from Windows hosts, Fluent Bit, NXLog, and Winlogbeat to OCSF 1.9 with one provider-aware operator, and it absorbs the former `sysmon` package. The Windows mappings carry the events and fields that stock Sigma rules match on, so the `sigma` operator can run those rules on normalized events. New operators also collect and normalize Microsoft Graph telemetry and translate OCSF events to Microsoft Sentinel ASIM.

## 💥 Breaking changes

### Unified Windows Event Log normalization

The standalone `sysmon` package is now part of the `microsoft` package. Use one provider-aware entry point for Sysmon and other Microsoft Windows Event Log events:

```tql
microsoft::windows::ocsf::normalize
```

For staged processing, use `microsoft::windows::canonicalize` followed by `microsoft::windows::ocsf::map`. The mapper dispatches by provider before event ID so event ID collisions cannot select a mapping for another provider.

*By @mavam and @codex in #180.*

## 🚀 Features

### Collector normalization

Normalize structured Windows Event Log events from Fluent Bit, NXLog, and Winlogbeat without collector-specific OCSF mappings. This includes Sysmon, Security, PowerShell, Defender, and other providers:

```tql
from_file "windows-events.nxlog.ndjson" {
  read_ndjson unflatten_separator="."
}
microsoft::windows::ocsf::normalize
metadata.log_format = "json"
```

Configure Fluent Bit with `event_data_as_map true` and `string_inserts false` to preserve named provider fields without positional duplicates. Configure NXLog with `AddPrefix TRUE` so provider fields remain distinct from collector metadata. Winlogbeat events use the structured `winlog` object and retain the remaining ECS fields under `unmapped.Winlogbeat`. The normalizer records the collector as a `metadata.loggers` entry and uses its receipt timestamp as `metadata.logged_time` when available. Direct Windows Event Log records use Windows Event Log as their logger.

The normalizer also accepts Windows Event Log XML directly. For staged processing, use `microsoft::windows::canonicalize` to produce the canonical Windows Event Log structure, then pass the result to `microsoft::windows::ocsf::map`. Add `metadata.log_format`, `raw_data`, and `raw_data_size` in the calling pipeline, where the source format and payload are known.

*By @mavam in #180.*

### Expanded Windows Event Log OCSF mapping

The `microsoft::windows::ocsf::normalize` operator now covers additional high-value Windows Event Log activity:

**PowerShell logging** (EIDs 4100/4103/4104/4105/4106) maps to OCSF Script Activity (1009). EID 4104 (Script Block Logging) sets `severity_id` to Low when AMSI flags the block; EID 4100 (engine error) marks the execution as a failure.

**Audit log cleared** (EID 1102) maps to OCSF Event Log Activity (1008, Clear) with `severity_id` set to High. Clearing the security log is a strong attacker indicator (MITRE ATT&CK T1070.001).

**Registry and object access** (EIDs 4657/4663) map registry value changes and audited file, registry, or other object access to their corresponding OCSF activity classes.

**Scheduled tasks** (EIDs 4698–4702) map create, delete, enable, disable, and update operations to OCSF Scheduled Job Activity (1006).

**Policy changes** (EIDs 4719/4739) map audit-policy and domain-policy updates to OCSF Entity Management (3004).

**Account Change** (EIDs 4720/4722–4726/4740/4767) covers create, enable, disable, delete, password change, password reset, lock, and unlock activities.

**Group Management** (EIDs 4727–4735/4737/4754–4758) covers global, local, and universal security group creation, deletion, updates, and membership changes.

**Group discovery** (EID 4799) maps local group membership enumeration to OCSF Live Evidence Info (5040).

**Remote Desktop denial** (EID 4825) maps rejected post-authentication RDP connections to OCSF RDP Activity (4005).

**Windows Firewall** (EIDs 4946/4948/4956/5024/5033) maps rule and profile changes plus successful service and driver starts.

**AppLocker** (EIDs 8001–8007) maps policy application and allowed, audited, or blocked application execution.

**Volume Shadow Copy** (VSSAudit EID 8222) maps shadow copy creation to OCSF File System Activity (1001).

**Microsoft Sentinel Common coverage** now includes 140 of the 143 event IDs in the Common set. The additional mappings cover Event Log health, Windows startup, security package loading, logoff and interactive sessions, privilege use, account and group changes, Kerberos, directory services, certificate services, network shares, NPS and wireless authentication, Group Policy application, peripherals, AD FS auditing, LSA group assignment, and Microsoft Entra Password Protection.

Together, these mappings cover all 39 events in Microsoft Sentinel's Minimal set and 140 events in its Common set. Provider-specific routes prevent overlapping event IDs from being attributed to unrelated Windows event sources. Common EIDs 1, 340, and 26401 remain unmapped because the Sentinel reference does not identify their providers or channels and no authoritative event manifests or public records could be found.

*By @mavam in #143, #147, and #182.*

### Microsoft Graph sources and OCSF mappings

The Microsoft package can now collect and normalize common Microsoft Graph security and inventory data.

Use the Graph source operators and `microsoft::graph::ocsf::normalize` for Entra ID sign-ins, directory audits, Defender alerts and incidents, Identity Protection risk data, and Intune inventory and compliance data.

Mapped events cover OCSF Authentication, Account Change, Group Management, Entity Management, Detection Finding, Incident Finding, Device Inventory Info, Software Inventory Info, and Compliance Finding classes.

*By @mavam and @codex in #147.*

### OCSF to ASIM mapper

The Microsoft package includes `microsoft::asim::from_ocsf` for translating validated OCSF 1.9 events into flat Microsoft Sentinel ASIM records. It takes an optional positional source field and a named `into` output, both defaulting to `this`.

Normalize a structured Windows Event Log or Microsoft Graph record before translating it to ASIM:

```tql
microsoft::windows::ocsf::normalize
microsoft::asim::from_ocsf
```

Use `microsoft::graph::ocsf::normalize` instead for Microsoft Graph records.

The ASIM translator covers authentication, process, audit, user-management, alert, file, network, DNS, DHCP, and web session schemas.

*By @mavam and @codex in #153.*

### Windows authorize session OCSF mapping

The `microsoft::windows::ocsf::normalize` operator now maps Windows Security Event ID 4672, "Special privileges assigned to new logon", to OCSF Authorize Session (3003) with the Assign Privileges activity.

*By @mavam and @codex in #148.*

### Windows event mappings for stock Sigma rules

The `microsoft::windows::ocsf::normalize` operator now carries the fields that stock SigmaHQ rules match on, so the `sigma` operator translates those rules onto the normalized events instead of skipping them.

**PowerShell** script block logging (EID 4104) stores the script text in `script.script_content.value`, and module logging (EID 4103) stores the pipeline payload there while the host application, user, command name, and script path come out of `ContextInfo`.

**Security log** object access now includes handle requests (EID 4656) next to performed accesses (EID 4663), with failed requests marked as such. Logon events (EIDs 4624/4625) carry the logon process and the requesting process, process creation (EID 4688) translates the mandatory label into `process.integrity_id` and names the account the process runs as, and directory service changes (EID 5136) name the modified attribute in `entity.data.attribute`.

**System log** service state changes (EID 7036) and start-type changes (EID 7040) map to Windows Service Activity, and event log clearing (EID 104) maps to Event Log Activity with the cleared channel in `log_name`.

**New providers**: Windows Firewall rule changes (EIDs 2004/2005/2006) map to Entity Management with a `firewall_rule` object, App Control block and audit events (CodeIntegrity EIDs 3023/3032/3033/3034/3036/3076/3077/3082/3104) map to Application Lifecycle, BITS transfer jobs (EID 16403) map to HTTP Activity, DNS client queries (EID 3008) map to DNS Activity with parsed answers, and AppX package deployments (EIDs 400/401/404) map to Application Lifecycle.

**Sysmon** process access (EID 10) stores the granted access mask in `requested_permissions`, DNS queries (EID 22) parse `QueryResults` into `answers`, and fingerprints with an algorithm OCSF does not enumerate, such as IMPHASH, keep the algorithm name next to the value.

*By @mavam.*

### Windows events for more stock Sigma rules

The `microsoft::windows::ocsf::normalize` operator now maps more Windows events that stock Sigma rules for Defender, Windows Firewall, AppX deployment, Code Integrity, and the Security and System logs match on. Previously, these events became OCSF Base Events, so stock rules for them never matched the normalized events.

**Microsoft Defender**: Restoring an item from quarantine (EID 1009) and deleting one (EID 1011) map to Detection Findings with the threat, the affected files, and the disposition. Deleted malware history (EID 1013), disabled malware or virus scanning (EIDs 5010 and 5012), blocked tamper attempts (EID 5013), and an expired antimalware platform (EID 5101) map to Detection Findings like the existing protection-state events.

**Windows Firewall**: The Windows 11 rule events (EIDs 2071 and 2097 added, 2073 modified, 2052 deleted) map like their earlier counterparts. Setting and profile changes (EIDs 2002, 2003, 2082, 2083), Group Policy updates and load failures (EIDs 2008 and 2009), resets to the default configuration (EIDs 2032 and 2060), and the deletion of all rules (EIDs 2033 and 2059) map to Entity Management events for the firewall policy, with the modifying user and application.

**AppX deployment**: Deployments that AppLocker or a deployment policy blocked (EIDs 412, 441, 442, 453, 454) map to failed installs. Started deployments (EID 603) and queued package URIs (EID 854) map to installs without a final status, keeping the deployment flags and the queued URIs.

**Code Integrity**: Loads of unsigned, revoked, or non-WHQL images and kernel modules (EIDs 3001, 3021, 3022, 3032, 3035, 3037, 3083) map to Application Lifecycle events that describe the load. EID 3032 previously counted as a block, but Windows reports it when it loads a revoked image.

**Security and System logs**: Created and deleted computer accounts (EIDs 4741 and 4743) map to Account Change, created and removed domain trusts (EIDs 4706 and 4707) map to Entity Management with the trusted domain as the entity, and services that terminate with an error (EID 7023) map to Windows Service Activity. Trusted domain policy changes (EID 4716) now also name the trusted domain.

AppX deployment and Code Integrity events no longer carry empty `application.url`, `application.product`, or `policy` objects, which violate OCSF. When the source event lacks these values, `application.url` and `application.product` are null and `policy` is absent.

*By @mavam.*

## 🔧 Changes

### Expanded OCSF 1.9 field coverage

Windows OCSF events now expose Kerberos service identities, ticket flags and complete PKINIT certificates; RDP session IDs; faulting modules and process-start times; and account display names and alternate IDs. Service start/type values are translated to OCSF enums, with unknown flag combinations preserved as Other. Sentinels, incomplete certificates, and vendor-specific context remain in `unmapped`.

*By @mavam in #191.*

### Sysmon OCSF 1.9 metadata

Sysmon mappings now target OCSF 1.9.0, the latest stable OCSF schema version used by the library.

Events produced by `microsoft::windows::ocsf::normalize` now advertise `metadata.version: "1.9.0"`. Review downstream validation, dashboards, and schema checks that matched on the previous OCSF metadata version.

*By @mavam and @codex in #147.*

### Windows collector diagnostics

Normalize Windows events from Winlogbeat and Fluent Bit without warnings when collector fields are absent or represented as strings. The Windows OCSF mapper now converts ports, IP addresses, result codes, logon types, file versions, and other collector-dependent values to their target types.

Correct OCSF mappings for source-specific authentication protocols, PowerShell script content, registry values of unknown type, Windows services, scheduled task actions, process sessions, and incomplete application or parent-process data.

Map rendered Windows messages from Winlogbeat, Fluent Bit, NXLog, and raw XML to the OCSF `message` field. Map source data to `raw_data` when an adapter provides it. Keep only collector details without an OCSF destination in `unmapped` instead of duplicating the event envelope.

*By @zedoraps.*

## 🐞 Bug fixes

### Microsoft Entra Conditional Access decisions in OCSF

Microsoft Entra sign-in events now preserve the Conditional Access decision in OCSF `authorizations`, keeping policy outcomes distinct from the overall authentication status.

Thanks to Wouter van Kranenburg for identifying the lost distinction.

*By @mavam in #184.*

### Windows and ASIM mappings without deprecation warnings

Windows event normalization and OCSF-to-ASIM file activity mapping no longer emit `contains` deprecation warnings on recent Tenzir versions. DNS record classification, user domain extraction, and file path classification remain unchanged.

*By @mavam in #190.*

### Windows normalization without `type_of` deprecation warnings

Windows event canonicalization and the Fluent Bit adapter no longer emit `type_of` deprecation warnings on Tenzir v6.20. Input format detection remains unchanged.

*By @IyeOnline in #200.*
