# Windows Event Log fixture sources

The following fixtures preserve the field names and representative values from
public Windows event records:

- EIDs 4699 through 4702: Microsoft Learn event reference examples at
  `https://learn.microsoft.com/windows/security/threat-protection/auditing/event-<id>`.
- EIDs 4719, 4739, 4799, and 4825: `mdecrevoisier/EVTX-to-MITRE-Attack`, from
  the matching `ID<id>-*.evtx` attack samples.
- EIDs 4735, 4737, 4744–4752, 4759–4764: Microsoft
  event schemas and representative values from
  `OTRF/OSSEM-DD/windows/etw-providers/Microsoft-Windows-Security-Auditing/events/event-<id>.yml`.
- EIDs 4657, 4663, 4740, 4767, 4946, 4948, 4956, 5024, and 5033: Microsoft
  Learn event reference examples at
  `https://learn.microsoft.com/windows/security/threat-protection/auditing/event-<id>`.
- EIDs 8001 through 8007: `detection.wiki` AppLocker examples, sourced from
  public Windows event captures including `NextronSystems/evtx-baseline`.
- EID 8222: the `detection.wiki` VSSAudit example for a created volume shadow
  copy.
- Microsoft-Windows-Security-Auditing Common-set events: Microsoft Learn audit
  event references at
  `https://learn.microsoft.com/windows/security/threat-protection/auditing/event-<id>`.
- AD FS Auditing EIDs 299, 324, 403, 404, 410–413, 431, 500, and 501:
  `https://detection.wiki/ad-fs-auditing/`.
- LsaSrv EID 300: the Microsoft-Windows-LSA manifest from
  `nasbench/EVTX-ETW-Resources` and the matching `detection.wiki` provider
  record.
- Microsoft Entra Password Protection EID 30004: the Microsoft Learn
  on-premises Password Protection monitoring reference and the public event
  record in `wazuh/wazuh#19441`.
- Microsoft Defender EIDs 1009 and 5012, Windows Firewall EID 2097, and
  AppXDeployment-Server EID 854: the field names of the EVTX samples in
  `SigmaHQ/sigma` under `regression_data/rules/windows/builtin/`, with
  synthetic values. Defender EID 1011 reuses the EID 1009 schema.
- Microsoft Defender EIDs 1013, 5010, 5013, and 5101, Windows Firewall EIDs
  2003, 2009, 2033, and 2052, AppXDeployment-Server EID 603, and
  CodeIntegrity EIDs 3001 and 3037: adapted from the provider event schemas
  and the fields that the matching `SigmaHQ/sigma` rules reference.
- AppXDeployment-Server EID 441: the Microsoft-Windows-AppXDeployment-Server
  manifest from `nasbench/EVTX-ETW-Resources`, whose message for the event has
  no parameters, so the fixture has an empty `EventData`.
- Security EIDs 4706, 4741, and 4743 and Service Control Manager EID 7023:
  Microsoft Learn event references at
  `https://learn.microsoft.com/windows/security/threat-protection/auditing/event-<id>`
  and the Service Control Manager message schema.
- `sigma/*.yml`: stock-shaped Sigma rules for the regression tests in
  `tests/sigma`. Each rule names the SigmaHQ rule whose logsource, event IDs,
  and fields it uses in `related`; the values are synthetic.
- Sentinel Common EIDs 1, 340, and 26401: no authoritative provider manifest or
  public event record was found. The coverage manifest keeps these IDs marked
  as unresolved rather than assigning them to a provider by number alone.

The EVTX records were converted to XML with `evtx_dump`. JSON and Microsoft
Learn records were normalized into standalone XML without changing their event
schema or representative values. When a public raw record was unavailable, the
fixture was adapted from the authoritative event schema and uses representative
values. The provider-aware coverage manifest in
`windows-sentinel-common-coverage.csv` records the source used for every event.
