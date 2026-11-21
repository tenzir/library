# Third-party test data

Some test inputs in this package contain data from other projects. All other
test inputs are synthetic.

## M57-Patents scenario

Source: [M57-Patents scenario](https://digitalcorpora.org/corpora/scenarios/m57-patents-scenario/)
by Digital Corpora. License:
[CC0 1.0](https://digitalcorpora.org/about-digitalcorpora/terms-of-use/).

The following files hold Suricata EVE records that Suricata wrote for the
scenario's network captures. They contain event metadata only, no captured
payloads.

| File | Changes |
|---|---|
| `inputs/alert.json` | None |
| `inputs/anomaly.json` | None |
| `inputs/dhcp.json` | None |
| `inputs/dns.json` | None |
| `inputs/fileinfo.json` | None |
| `inputs/flow.json` | None |
| `inputs/ftp.json` | None |
| `inputs/http.json` | None |
| `inputs/smb.json` | None |
| `inputs/smtp.json` | None |
| `inputs/tls.json` | None |
| `ocsf/tls-sslv3-certificate.input` | Timestamps shifted |
| `ocsf/tls-sslv2-certificate.input` | Timestamps shifted, TLS version changed to SSLv2 |
| `ocsf/tls-ip-server-name-handshake.input` | Timestamps shifted, server address added as SNI |
