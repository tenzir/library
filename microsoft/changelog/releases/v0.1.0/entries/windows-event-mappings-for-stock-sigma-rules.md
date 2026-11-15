---
title: Windows event mappings for stock Sigma rules
type: feature
authors:
  - mavam
created: 2026-09-03T21:30:00Z
---

The `microsoft::windows::ocsf::normalize` operator now carries the fields that
stock SigmaHQ rules match on, so the `sigma` operator translates those rules
onto the normalized events instead of skipping them.

**PowerShell** script block logging (EID 4104) stores the script text in
`script.script_content.value`, and module logging (EID 4103) stores the
pipeline payload there while the host application, user, command name, and
script path come out of `ContextInfo`.

**Security log** object access now includes handle requests (EID 4656) next to
performed accesses (EID 4663), with failed requests marked as such. Logon
events (EIDs 4624/4625) carry the logon process and the requesting process,
process creation (EID 4688) translates the mandatory label into
`process.integrity_id` and names the account the process runs as, and directory
service changes (EID 5136) name the modified attribute in
`entity.data.attribute`.

**System log** service state changes (EID 7036) and start-type changes (EID
7040) map to Windows Service Activity, and event log clearing (EID 104) maps to
Event Log Activity with the cleared channel in `log_name`.

**New providers**: Windows Firewall rule changes (EIDs 2004/2005/2006) map to
Entity Management with a `firewall_rule` object, App Control block and audit
events (CodeIntegrity EIDs 3023/3032/3033/3034/3036/3076/3077/3082/3104) map to
Application Lifecycle, BITS transfer jobs (EID 16403) map to HTTP Activity, DNS
client queries (EID 3008) map to DNS Activity with parsed answers, and AppX
package deployments (EIDs 400/401/404) map to Application Lifecycle.

**Sysmon** process access (EID 10) stores the granted access mask in
`requested_permissions`, DNS queries (EID 22) parse `QueryResults` into
`answers`, and fingerprints with an algorithm OCSF does not enumerate, such as
IMPHASH, keep the algorithm name next to the value.
