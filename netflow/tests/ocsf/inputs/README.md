# NetFlow test fixtures

These binary captures come from the `read_netflow` integration tests in the
Tenzir engine repository. They exercise the package mapper together with the
wire decoder.

| Fixture | Coverage |
| --- | --- |
| `unusual_traffic.nfv5` | NetFlow v5 fixed records |
| `cisco.nfv9` | NetFlow v9 template-based records |
| `mikrotik.ipfix` | IPFIX records with IPv4, IPv6, and NAT fields |
| `threats.ixflow` | IPFIX options records |
