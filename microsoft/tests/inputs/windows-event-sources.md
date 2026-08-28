# Windows Event Log fixture sources

The following fixtures preserve the field names and representative values from
public Windows event records:

- EIDs 4699 through 4702: Microsoft Learn event reference examples at
  `https://learn.microsoft.com/windows/security/threat-protection/auditing/event-<id>`.
- EIDs 4719, 4739, 4799, and 4825: `mdecrevoisier/EVTX-to-MITRE-Attack`, from
  the matching `ID<id>-*.evtx` attack samples.
- EIDs 4735 and 4737: Microsoft event schemas and sample values from
  `OTRF/OSSEM-DD/windows/etw-providers/Microsoft-Windows-Security-Auditing/events/event-4735.yml`
  and `event-4737.yml`.
- EIDs 4740 and 4767: Microsoft Learn event reference examples at
  `https://learn.microsoft.com/windows/security/threat-protection/auditing/event-<id>`.

The EVTX records were converted to XML with `evtx_dump`. The Microsoft Learn
records were normalized into standalone XML without changing their event data.
