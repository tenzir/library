# Demo replay

All feeds replay a finite recording as an endless live stream:

| Operator | Recording | Cycle | Events per second |
| --- | --- | --- | ---: |
| `demo::zeek` | Ships with the package | 3 min | 1.0 |
| `demo::suricata` | Ships with the package | 3 min | 1.4 |
| `demo::openssh` | Hosted, 1,581 records | 4 min | 6.2 |
| `demo::windows "xml"` | Hosted, 105 records | 130 s | 0.8 |
| `demo::windows "winlogbeat"` | Hosted, 105 records | 65 s | 1.6 |
| `demo::windows "fluent-bit"` | Hosted, 105 records | 53 s | 2.0 |
| `demo::claude_code` | Hosted, 469 records | 9 min | 0.9 |
| `demo::codex` | Hosted, 1,782 records | 28 min | 1.1 |

Within one cycle, records keep their recorded spacing, timestamps keep their
relation to each other, and equal identifiers stay equal. Long pauses in a
recording are cut. The next cycle continues without a gap and with fresh
identifiers.

All feeds take the same arguments:

| Argument | Default | Description |
| --- | --- | --- |
| `speed` | `1.0` | Multiplies the rate. Durations inside a record stay unchanged. |
| `start` | shared clock | Start of the first cycle. Use `now()` to start with the first record. |
| `seed` | `""` | Changes the identifiers, for example per deployment. |
| `cycles` | endless | Number of cycles. |
| `pace` | `true` | Emit records at their replayed time instead of immediately. |

By default, all pipelines share one clock: two pipelines emit equal records at
the same time, and a restarted pipeline continues in the middle of a cycle
without repeating records. The first record can take up to the longest pause of
the feed.

Hosted recordings are downloaded once, when the pipeline starts. A pipeline that
can't download its recording fails to start; a running feed needs no network.

## Replay your own recording

`demo::replay::run` expects events with the recording time in `time` and the
record in `raw`. It moves all ISO timestamps in `raw`. Mark the identifiers that
every cycle should renew:

```tql
from_file "/recordings/app.log" {
  read_lines
}
raw = move line
time = raw.split(" ")[0].time()
demo::replay::mark raw, "(session=)([0-9a-f]+)", "hex"
demo::replay::run max_gap=30s
```

Use `demo::openssh::replay`, `demo::windows::replay`, and
`demo::agents::replay` for recordings of these sources.

## Zeek and Suricata samples

`scripts/build_samples.py` writes `operators/zeek/sample.tql` and
`operators/suricata/sample.tql`. It runs both sensors offline over traffic from
`scripts/make_traffic.py`, which uses documentation addresses and `.example`
names only. Both samples describe the same connections, and Suricata alerts come
from `scripts/demo.rules`.

Before publishing a recording, run `scripts/check.py privacy` on it and
`scripts/check.py replay` on two replayed cycles.
