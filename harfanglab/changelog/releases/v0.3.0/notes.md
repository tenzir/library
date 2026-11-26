OCSF events fetched from HarfangLab now keep HarfangLab's log type.

## 🚀 Features

### HarfangLab log type in OCSF events

OCSF events from `harfanglab::fetch` now carry HarfangLab's log type, such as `dns_resolution` or `raw_socket_creation`, in `metadata.log_name`. Several log types share an OCSF class, so this is the only way to tell them apart. The Splunk export names the log type only in the envelope that `fetch` removes.

*By @zedoraps in #278.*
