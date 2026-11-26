---
title: HarfangLab log type in OCSF events
type: feature
authors:
  - zedoraps
prs:
  - 278
created: 2026-11-26T22:03:09.506604Z
---

OCSF events from `harfanglab::fetch` now carry HarfangLab's log type, such as `dns_resolution` or `raw_socket_creation`, in `metadata.log_name`. Several log types share an OCSF class, so this is the only way to tell them apart. The Splunk export names the log type only in the envelope that `fetch` removes.
