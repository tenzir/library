---
title: More Zeek log types in OCSF mappings
type: feature
authors:
  - zedoraps
created: 2026-11-26T01:38:19.117838Z
---

The Zeek OCSF mappings now cover many more log types instead of falling back to Base Event:

- NTP Activity for `ntp.log`, with the activity from the NTP mode.
- Authentication for `kerberos.log`, `ntlm.log`, `radius.log`, and LDAP binds in `ldap.log`. Records without a user stay Network Activity.
- `files.log` maps to the class of the protocol that carried the file: HTTP Activity, SMB Activity, FTP Activity, or Email Activity, with names, MIME types, sizes, and hashes. Other protocols map to Network Activity.
- SMB Activity for `smb_mapping.log` and `smb_cmd.log`, and Tunnel Activity for `tunnel.log`.
- Detection Finding for `intel.log`, `signatures.log`, and `notice_alarm.log`.
- Software Inventory Info for `software.log` and Device Inventory Info for `known_hosts.log`.
- Network Activity for `snmp.log`, `sip.log`, `syslog.log`, `analyzer_debug.log`, `dpd.log`, and application protocol logs such as `mysql.log`, `postgresql.log`, `modbus.log`, `dnp3.log`, `modbus_register_change.log`, `mqtt_*.log`, `quic.log`, and `socks.log`.
