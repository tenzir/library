# Third-party test data

Some test inputs in this package contain data from other projects. All other
test inputs are synthetic.

## M57-Patents scenario

Source: [M57-Patents scenario](https://digitalcorpora.org/corpora/scenarios/m57-patents-scenario/)
by Digital Corpora. License:
[CC0 1.0](https://digitalcorpora.org/about-digitalcorpora/terms-of-use/). The
license statement excludes material that explicitly claims a copyright,
including in packet dumps.

The following files hold Suricata EVE records of the scenario's network
captures from November 2009. They contain event metadata only, no payload or
packet fields.

| File | Changes |
|---|---|
| `inputs/alert.json` | Times written with `Z` |
| `inputs/anomaly.json` | Times written with `Z` |
| `inputs/dhcp.json` | Times written with `Z` |
| `inputs/dns.json` | Times written with `Z` |
| `inputs/fileinfo.json` | Times written with `Z` |
| `inputs/flow.json` | Times written with `Z`; one is off by a nanosecond |
| `inputs/ftp.json` | Times written with `Z` |
| `inputs/http.json` | Times written with `Z` |
| `inputs/smb.json` | Times written with `Z` |
| `inputs/smtp.json` | Times written with `Z` |
| `inputs/tls.json` | Times written with `Z`; one is off by a nanosecond |

The table lists the differences from Suricata's EVE format that the files
themselves show. The records were not compared with the captures. The files
have not changed since they joined this repository.
