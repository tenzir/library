# Test inputs

All inputs are synthetic. They follow the shapes that a HarfangLab Manager 6.2
returns from its pull exports, with invented values: documentation IP ranges
(RFC 5737, RFC 3849), `example.com` domains, and made-up UUIDs and host names.

- `pull/splunk/`: pages of the Splunk export, JSON arrays of HEC envelopes that
  wrap OCSF 1.6.0 events.
- `pull/elastic/`: pages of the Elastic export, JSON arrays of ECS documents.

The `harfanglab_manager` fixture serves one file per request in name order,
then an empty body, like a drained queue. `03.json` is the `[]` that a
Manager may also return for an empty queue.
