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
| [detect-pii.tql](examples/detect-pii.tql) | Assesses synthetic raw logs containing an email address, a name and phone number, or metrics. |
| [detect-pii-ocsf.tql](examples/detect-pii-ocsf.tql) | Sends complete OCSF events, asks about email addresses and names, and separately identifies populated identity fields. |
| [score-investigation-priority.tql](examples/score-investigation-priority.tql) | Estimates investigation priority against three ordered criteria for analyst review. |
| [score-commands-batched.tql](examples/score-commands-batched.tql) | Collects command-risk questions in a window, sends one standard request per window, and maps scores back to commands. |

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

### Connect directly to hosted Jev

Create a managed secret named `JEV_API_KEY` containing your Typesafe API key.
For direct access to Jev, use the settings from the
[Typesafe quickstart](https://docs.typesafe.ai/introduction/quickstart):

```tql
let $url = "https://api.typesafe.ai/v1/systemone"
let $model = "jev-latest"
let $api_key_secret_name = "JEV_API_KEY"
```

Set these values in the installed package's `constants.tql` and restart the
node, or pass `url`, `model`, and `api_key_secret_name` to individual operator
calls. All five examples work with these settings.

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
fields and sets `answers`, `array`, and `usage`, replacing those fields if
present. `answers` is a record keyed by question ID. `array` is a list of the
same answers, each with an `id` field. It follows response field order, which
is not guaranteed to match question order. Sort it in the calling pipeline
when order matters. Mixed answer types share a list schema, so fields absent
from an answer can appear as nulls in `array`; the `answers` record retains
the original answer shapes.

Supported types are `noul`, `choice`, and `score`. `noul` returns a probability;
`choice` selects a supplied option; `score` returns an expected index into an
ordered list of criteria. Requests run sequentially within each operator call
to avoid a concurrent HTTP subpipeline hang observed with Tenzir 6.19. This
limits throughput to one active request per operator instance. Combine questions
in one request to reduce the number of HTTP requests.

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

## Combine questions in one request

Use [score-commands-batched.tql](examples/score-commands-batched.tql) for a
complete pipeline with `window`, `summarize`, `jev::collect_record`, and
`jev::ask`. It works with the configured System One endpoint, including hosted
Jev and local Laya.

The example uses `window gap=2s, size=25, on=time`. It groups commands until
the event-time gap exceeds two seconds or the window reaches 25 events. Its
three sample commands form two requests. The final partial window closes when
the input ends. With event time, silence alone does not advance the clock;
omit `on=time` to use arrival time and close sessions after wall-clock inactivity.

Each command becomes a question with a unique key within its window. After
collecting the questions into a record, `jev::ask` sends one request and the
pipeline sorts `array` by numeric ID and pairs it with `events` using `zip`.
It checks the counts and each pair's ID before emitting events. A mismatch
emits a warning and drops the entire window's result. Five ordered criteria
produce an expected index from 0 to 4, which the example scales to a 0–100 risk score.
The score is an estimate for analyst review, not an OCSF severity identifier.

`request_usage` describes the entire request and is repeated on each output
event. All questions share one state; assess model quality with this layout
before using it for decisions.

Windowing, collection, and matching answers back to events happen in your
pipeline. `jev::ask` sends one request per input event; it does not create
windows or buffer events into groups.

## Build dynamic question records

`jev::collect_record entries` converts a list of `{key, value}` records in place.
It is a non-Nova workaround for the built-in `collect_record` function.
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

Moving logs from `state` into question instructions changed Laya's behavior
in testing. Validate batched question results separately from single-event
results on your chosen model.

## Test the package

```sh
uvx tenzir-test jev
```

The registered [HTTP fixture](fixtures/jev_api.py) supplies deterministic
responses, dummy secrets, and assertions on actual requests. Tests cover all
question types, connection overrides, no-key operation, input preservation,
full and partial question batches, event order, answer lists, guarded pairing,
and question-record construction. They do not call hosted services or assess model accuracy.
The examples are also exercised against the real local service.
