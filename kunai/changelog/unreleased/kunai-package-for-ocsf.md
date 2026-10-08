---
title: Kunai package for OCSF
type: feature
authors:
  - mavam
prs:
  - 193
created: 2026-10-08T09:46:58.308309Z
---

The library now includes a `kunai` package that maps events from [Kunai](https://why.kunai.rocks), the eBPF-based security monitor for Linux, to OCSF 1.9.0.

Kunai writes one JSON object per event, which Tenzir reads natively, so you only need the normalizer:

```tql
from_file "kunai.log" {
  read_ndjson
}
kunai::ocsf::normalize
```

The package maps every event type that Kunai defines:

| Kunai events | OCSF class |
|---|---|
| `execve`, `execve_script`, `clone`, `exit`, `exit_group`, `kill`, `ptrace`, `prctl`, `commit_creds`, `creds_tampered` | Process Activity |
| `read`, `read_config`, `write`, `write_config`, `write_close`, `file_create`, `file_unlink`, `file_rename` | File System Activity |
| `connect`, `send_data` | Network Activity |
| `dns_query` | DNS Activity |
| `init_module`, `bpf_prog_load`, `bpf_socket_filter` | Kernel Extension Activity |
| `mmap_exec` | Module Activity |
| `mprotect_exec` | Memory Activity |
| `io_uring_sqe` | Kernel Activity |
| `file_scan` with a YARA match | Detection Finding |
| `start` | Application Lifecycle |
| `error`, `event_loss` | Application Error |

Events that one of Kunai's detection rules matched become alerts in the OCSF Security Control profile. The rule severity and the ATT&CK identifiers carry over.

The mapping reads the event layout of Kunai releases up to 0.7.0-rc.1 as well as the layout of the development version, which nests the user credentials and writes the process ancestors as a list.
