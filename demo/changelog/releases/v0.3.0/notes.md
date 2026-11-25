This release adds operators that generate synthetic OCSF 1.9 events for demos, lookup benchmarks, and robustness tests.

## 🚀 Features

### Synthetic OCSF workload generation

The `demo` package now generates synthetic OCSF 1.9 events for Base Event and 45 classes from a recurring organization of users, workstations, and services, for demos, lookup benchmarks, and robustness tests. Events from sources with a native log format, such as Zeek, Sysmon, or CloudTrail, carry that log in `raw_data`.

```tql
demo::ocsf::generate count=100000
```

- `demo::ocsf::generate` emits an exact number of events, optionally with exact counts of IOC needles.
- `demo::ocsf::generate_load` emits a continuous stream at a given rate.
- `demo::ocsf::generate_historical` covers past days with office-hours and off-hours rates.
- `demo::ocsf::generate_legacy` emits OCSF 1.6 events for five classes to test mixed schema versions.

*By @zedoraps in #207.*
