# Windows Event Log fixtures

All Windows fixtures in this directory are synthetic. Each record keeps the
structure that Windows and the collectors write for its event, and invents
every value.

The structure that the fixtures keep:

- Provider name and GUID, event ID, version, level, task, opcode, keywords,
  and channel.
- Field names, field order, and positional layouts where a test reads data
  without names, such as Application Error 1000 and Windows Error Reporting
  1001.
- Binary encodings, such as the SYSTEMTIME in EventLog 6005, the UTF-16
  service names of Service Control Manager events, and the binary creator SID
  in WMI-Activity 5861.
- Collector shapes: Windows Event XML, Fluent Bit JSON with local timestamps,
  rendered messages, and string inserts, Winlogbeat JSON with the original XML,
  and NXLog JSON.
- Well-known values that carry meaning, such as built-in SIDs, audit
  subcategory GUIDs, device class GUIDs, attack surface reduction rule GUIDs,
  message-table tokens, and status codes.

The invented values use the `example.test` domain with the NetBIOS name
`EXAMPLE`, documentation SIDs such as
`S-1-5-21-1111111111-2222222222-3333333333-500`, documentation IP addresses,
and generated GUIDs, hashes, process IDs, record IDs, and times. Workgroup
machines keep a bare host name, as Windows writes it for them.

Each fixture with a leading comment names the event and the template it
follows. `sigma/*.yml` holds stock-shaped Sigma rules whose values match these
fixtures; each rule names the SigmaHQ rule whose logsource, event IDs, and
fields it uses in `related`. The coverage manifest
`windows-sentinel-common-coverage.csv` maps every event of the Microsoft
Sentinel Common set to its mapping and fixture. Sentinel Common EIDs 1, 340,
and 26401 stay unresolved because no provider is known for them.
