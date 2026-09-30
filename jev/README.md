# Jev

Ask typed security questions through Jev or a compatible System One API. The
package includes five runnable examples and supports local inference with Laya.

## Run locally in Explorer

The local service and package are installed on `tenzir-node-staging`:

- Tenzir 6.19.0 runs the pipelines and connects to the platform.
- Laya 0.3.22 serves the English checkpoint on the private container network.
- The installed package uses `http://tenzir-laya:8000/v1/systemone` and the
  node's existing `LAYA_API_KEY` managed secret.

Select **tenzir-node-staging** in Explorer and paste one of these files unchanged:

| Example | What it does |
| --- | --- |
| [classify-ocsf.tql](examples/classify-ocsf.tql) | Suggests an OCSF class for authentication, HTTP, and unknown logs. Preserves the raw log and option probabilities. |
| [classify-ocsf-batched.tql](examples/classify-ocsf-batched.tql) | Classifies the same logs in one native batch request, preserving each log as an independent state. |
| [detect-pii.tql](examples/detect-pii.tql) | Assesses synthetic raw logs containing an email address, a name and phone number, or metrics. |
| [detect-pii-ocsf.tql](examples/detect-pii-ocsf.tql) | Sends complete OCSF events, asks about email addresses and names, and separately identifies populated identity fields. |
| [score-investigation-priority.tql](examples/score-investigation-priority.tql) | Estimates investigation priority against three ordered criteria for analyst review. |

Replace each example's `from` source with your input stream to use your own
logs. The original data and model usage remain available in the output.

The examples return model estimates. They do not discard events, redact values,
create complete OCSF mappings, or treat a low probability as proof of no PII.

## Configure another installation

Install the `jev/` directory in the node's package directory. To use local Laya,
set the installed package's `constants.tql` to the following values, then restart
the node:

```tql
let $url = "http://tenzir-laya:8000/v1/systemone"
let $model = "english"
let $api_key_secret_name = "LAYA_API_KEY"
```

The hostname must be reachable from the Tenzir process. On a host where both
processes run directly, use `http://127.0.0.1:8000/v1/systemone` instead.
For a server without authentication, use `let $api_key_secret_name = ""`.
An empty string skips secret lookup and omits the Authorization header.

The source package's [constants.tql](constants.tql) defaults to Jev through
Vercel. The installed local copy uses the settings shown above. You can override
the connection per call without editing constants:

```tql
jev::ask questions,
  url="http://127.0.0.1:8000/v1/systemone",
  model="english",
  api_key_secret_name="",
  state=raw
```

`api_key_secret_name` names a managed secret; do not put the key value there.
Omitting an argument or passing `null` uses the package default. The examples use the
configured defaults so they need no connection edits on staging.

## Ask one typed question

Use `jev::noul`, `jev::choice`, or `jev::score` to ask one question without
constructing a question record:

```tql
from {raw: "Login succeeded for alex.morgan@example.com"}
jev::noul "Does this log contain personal data?", state=raw
```

Each operator preserves input fields and sets `answer` to the complete typed
answer and `usage` to the request usage, replacing those fields if present.
Existing `questions` and `answers` fields are preserved. Read `answer.noul`
for the probability, `answer.choice` and `answer.probabilities` for the selected
option and its distribution, or `answer.score` and `answer.legend` for the
expected index and ordered criteria.

`choice` takes a record of named options after the instructions:

```tql
from {raw: "sshd: Failed password for user alex"}
jev::choice "Which OCSF class best fits this log?",
  {"3002": "Authentication", unknown: "Insufficient evidence or another class"},
  state=raw
```

`score` takes an ordered list of descriptions. Three criteria produce an
expected index between 0 and 2, which is not an OCSF severity identifier:

```tql
from {raw: "An administrator disabled audit logging"}
jev::score "How urgently should an analyst investigate this activity?",
  ["Routine review", "Investigate soon", "Investigate immediately"],
  state=raw
```

Instructions and criteria can be expressions evaluated for each event. All
three operators reuse `jev::ask` and accept its `state`, `url`, `model`, and
`api_key_secret_name` options with the same defaults. Each call sends one request
per event. To keep an answer across subsequent calls, save it to another field first.
For multiple questions in one request, use `jev::ask`.

## Ask multiple questions about one event

`jev::ask questions, state=raw` submits a question record and one string state
using the [System One API](https://docs.typesafe.ai/api). It preserves input
fields and sets `answers` and `usage`, replacing those fields if present.

Supported types are `noul`, `choice`, and `score`. `noul` returns a probability;
`choice` selects a supplied option; `score` returns an expected index into an
ordered list of criteria. Requests run sequentially within each operator call
to avoid a concurrent HTTP subpipeline hang observed with Tenzir 6.19. This
limits throughput to one active request per operator instance; use native
batching to assess multiple independent states in that request.

For a complete event, snapshot it before adding questions:

```tql
this = {event: this}
questions = {email: {
  type: "noul",
  instructions: "Does this event contain a personal email address?",
}}
jev::ask questions, state=print_json(event)
```

The OCSF PII example preserves the nested event and lists populated
`user.email_addr` and `user.full_name` fields independently of model predictions.
Extend that inventory for your sources. Whole-event model answers do not
identify exact fields or character spans for redaction.

## Batch independent events

`jev::ask_batch states, questions` uses Laya's native `/v1/systemone/batch`
contract: a list of independent states and a shared question record. Its default
URL is the configured System One URL plus `/batch`; override `url` if needed.
This extension requires a compatible batch server. It is not a feature of every
System One endpoint.

The operator preserves input fields and sets `results` and `total_usage`.
Results follow input-state order, and each result includes its own answers and
usage. A response with a different result count emits a warning and drops that
batch, preventing the example from pairing an incomplete response with logs.

The batched example uses `window size=64`, `summarize events=collect(this)`, and
`states=events.map(e => e.raw)`. It calls the batch operator once and pairs
`events` with `results` using `zip`. Laya permits at most 64 states per request.
The three sample logs therefore produce one HTTP request.

A finite source flushes its final partial batch when it ends. To flush partial
batches on a live stream at five-second boundaries, wrap the count window:

```tql
window size=5s {
  window size=64 {
    // Collect events, ask_batch, and pair results as in the example.
  }
}
```

Inference adds latency after a window closes. The `batch` operator controls
internal buffering and does not itself combine API requests.

## Build dynamic question records

`jev::collect_record entries` converts a list of `{key, value}` records in place.
Keys must be strings; values must be JSON-compatible. Keys are sorted, the last
value wins for duplicates, and explicit nulls are preserved. Empty lists become
`{}`; null lists remain null. Do not submit empty question records to the API.

Keep different question schemas in separate lists, collect each into a record,
then merge the records. TQL gives records in a list a shared schema and adds
nulls for missing fields. Mixing unrelated choice criteria in one list can
therefore add unintended null options before either package operator runs.
The tests verify the exact HTTP body for safely merged question families.

## Detection limits

Keep model usage in the output. Laya reports `truncated` and
`truncated_questions` when part of a state did not fit. Other servers may omit
these fields. Missing metadata does not establish that the whole event was read.

Laya's results depend on input layout, formatting, and context length. The
raw-log PII example distinguished its positive and negative samples, but the
complete-event example also produced a false positive for a person name in a
service-account event at a 0.5 threshold. In a controlled long-event check,
placing identity fields beyond the context limit reduced the PII score from
about 0.80 to 0.14. These examples demonstrate integration, not production
accuracy. Calibrate decisions on labeled events from your sources.

The batch example keeps each log in `state`. Moving logs into question
instructions to fit unrelated events into one standard request changed the
model's behavior in testing. Native independent-state batching matched the
single-event results on the tested inputs.

## Test the package

```sh
uvx tenzir-test jev
```

The registered [HTTP fixture](fixtures/jev_api.py) supplies deterministic
responses, dummy secrets, and assertions on actual requests. Tests cover all
question types, connection overrides, no-key operation, input preservation,
full and partial batches, result matching, malformed result counts, and
question-record construction. They do not call hosted services or assess model
accuracy. The examples are also exercised against the real local service.
