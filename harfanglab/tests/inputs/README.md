# Test inputs

All inputs are synthetic. They follow the shapes that a HarfangLab Manager 6.2
returns from its pull exports, with invented values: documentation IP ranges
(RFC 5737, RFC 3849), `example.com` domains, and made-up UUIDs and host names.

- `pull/splunk/`: pages of the Splunk export, JSON arrays of HEC envelopes that
  wrap OCSF 1.6.0 events.
- `pull/elastic/`: pages of the Elastic export, JSON arrays of ECS documents.
- `ocsf/` and `ecs/`: NDJSON files of single OCSF 1.6.0 events and ECS
  documents, as `harfanglab::fetch` returns them, for the reduction
  operators. Their timestamps start at 2026-01-01 and place events on both
  sides of window boundaries. `edge.ndjson` holds the edge cases: missing and
  null keys, Listen events, a late event, an executable without hashes, a
  raw socket creation (OCSF), starts that differ only in the real user, and a
  library without hashes (ECS).

The reduction operators window by processing time, and a test that runs
across a wall-clock window boundary splits a summary in two. A test run takes
a fraction of a second against windows of five minutes or more, so this is
rare.

The `harfanglab_manager` fixture serves one file per request in name order,
then an empty body, like a drained queue. `03.json` is the `[]` that a
Manager may also return for an empty queue.

The `harfanglab::ioc::sync` tests use inline indicators instead: documentation
IP addresses, `example.*` domains, and hashes of well-known strings. The
fixture keeps their IOC sources and rules in memory.
