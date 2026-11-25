# Demo replay

All feeds replay a short recording as an endless live stream:

| Operator | Recording | Output | Cycle | Events per second |
| --- | --- | --- | --- | ---: |
| `demo::zeek` | 3,143 events in 22 logs | as `read_zeek_tsv` | 20 min | 2.6 |
| `demo::suricata` | 3,654 events of 17 types | as `read_suricata` | 20 min | 3.0 |
| `demo::openssh` | 1,581 records of 7 hosts | as `read_syslog raw_message=raw` | 4 min | 6.8 |
| `demo::windows "winlogbeat"` | 105 records | as `read_ndjson` | 68 s | 1.5 |
| `demo::windows "fluent-bit"` | 105 records | as `read_ndjson` | 56 s | 1.9 |
| `demo::windows "xml"` | 105 records | the XML in `data`, as `read_delimited "</Event>\n"` | 140 s | 0.8 |
| `demo::claude_code` | 469 records | as `accept_otlp` with `schema="record"` | 9 min | 0.8 |
| `demo::codex` | 1,782 records | as `accept_otlp` with `schema="record"` | 29 min | 1.0 |

The recordings are files as the collectors write them. A feed downloads its file,
reads it, replays it, and, where the records are text, parses it. Except for times
and identifiers, the output is what you get from the file or the collector
directly.

Events keep their recorded spacing, timestamps keep their relation to each other,
and equal identifiers stay equal within one cycle. The next cycle follows without
a gap and with new identifiers.

All feeds take the same arguments:

| Argument | Default | Description |
| --- | --- | --- |
| `speed` | `1.0` | Multiplies the rate. Durations inside an event stay unchanged. |
| `cycles` | endless | Number of cycles. |

A feed begins with the first event of the recording when its pipeline starts, and
again after a restart. Identifiers depend on the start of the cycle, so two
pipelines and two starts give different ones.

A feed downloads its recording once, when the pipeline starts. It fails to start
without network, and needs none afterwards.

`demo::windows` also gives every cycle one of three host names. See
[agents.md](agents.md) for the agent recordings.

## Zeek and Suricata

Zeek 8.0.10 and Suricata 8.0.3 recorded the same 20 minutes of generated traffic
of an invented office, with documentation addresses and `.example` names only.
Both see the same connections; join them on `community_id`. A small incident runs
through both: a mail with a link, a download, a beacon, DNS tunneling, scans,
password guessing, file access, and uploads.

## Replay your own short recording

Use `demo::replay::events` for parsed events. It moves all time fields and renews
the identifiers in the named fields:

```tql
from_file "/recordings/conn.log" {
  read_zeek_tsv
}
time = ts
demo::replay::events ids=["uid"]
```

Use `demo::replay::run` for raw records, which keep their text. It moves all ISO
timestamps in `raw` and renews the identifiers that you select:

```tql
from_file "/recordings/app.log" {
  read_lines
}
raw = move line
time = raw.split(" ")[0].time()
demo::replay::renew_ids raw, "(session=)([0-9a-f]+)", kind="hex"
demo::replay::run
select raw
write_lines
```

`demo::zeek::replay`, `demo::suricata::replay`, `demo::openssh::replay`,
`demo::windows::replay`, and `demo::agents::replay` do this for their sources. Set
`start` to begin at another time than now; records before now come at once.

Both operators keep the recording in memory and fail beyond `max_events`, 20,000
by default. 10,000 records of 0.5 KB take about 80 MiB at the peak, 100,000 about
450 MiB.

## Replay a large recording

Large recordings need neither endless cycles nor new identifiers. Replay them with
the built-in operators, which stream:

```tql
from_file "/recordings/eve.json" {
  read_suricata
}
reorder on=timestamp, tolerance=1min
timeshift timestamp, start=now()
delay timestamp
```

A recording of 1,000,000 events and 518 MB took about 430 MiB of memory, constantly. This
replay

- ends with the recording,
- moves only the given time field, not nested times or times in text,
- keeps identifiers and long pauses, and
- drops events that are later than `tolerance`.
