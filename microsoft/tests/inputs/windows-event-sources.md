# Windows Event Log fixture sources

The following fixtures preserve the field names and representative values from
public Windows event records:

- EIDs 4699 through 4702: Microsoft Learn event reference examples at
  `https://learn.microsoft.com/windows/security/threat-protection/auditing/event-<id>`.
- EIDs 4719, 4739, 4799, and 4825: `mdecrevoisier/EVTX-to-MITRE-Attack`, from
  the matching `ID<id>-*.evtx` attack samples.
- EIDs 4735, 4737, 4744–4746, 4750–4752, 4760–4762, and 4764: Microsoft
  event schemas and representative values from
  `OTRF/OSSEM-DD/windows/etw-providers/Microsoft-Windows-Security-Auditing/events/event-<id>.yml`.
- EIDs 4657, 4663, 4740, 4767, 4946, 4948, 4956, 5024, and 5033: Microsoft
  Learn event reference examples at
  `https://learn.microsoft.com/windows/security/threat-protection/auditing/event-<id>`.
- EIDs 8001 through 8007: `detection.wiki` AppLocker examples, sourced from
  public Windows event captures including `NextronSystems/evtx-baseline`.
- EID 8222: the `detection.wiki` VSSAudit example for a created volume shadow
  copy.

The EVTX records were converted to XML with `evtx_dump`. JSON and Microsoft
Learn records were normalized into standalone XML without changing their event
schema or representative values.
