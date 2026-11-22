This first release maps OCSF 1.9 events to Splunk CIM datasets with `splunk::cim::from_ocsf`, including Windows events from the microsoft package.

## 🚀 Features

### OCSF to Splunk CIM mapping

`splunk::cim::from_ocsf` maps OCSF 1.9 events to Splunk CIM datasets:

```tql
splunk::cim::from_ocsf ocsf, into=cim
```

- Datasets: Authentication, Change and Account Management, Endpoint Processes, Filesystem, Registry, and Services, Network Traffic, Network Resolution (DNS), Network Sessions (VPN), Web, Email, Malware, Alerts, Vulnerabilities, Data Access, and Database Query.
- Fields use CIM 8.x names and values, such as `action=created` or `action=allowed`, and multivalue fields, such as group members, are lists.
- Windows events from the microsoft package get their title as `signature`, the logon type as `authentication_method` and `app`, their domains, and the account a process runs as.
- OCSF events that carry only IDs get their captions derived first.

*By @zedoraps.*
