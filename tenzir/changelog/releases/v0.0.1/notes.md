## 💥 Breaking changes

### Consolidated Tenzir utility packages

OSINT enrichment and OCSF trimming utilities now live in the `tenzir` package.

Use the new namespaced utility operators in your pipelines:

```tql
tenzir::osint::enrich
tenzir::ocsf::trim
```

Installations that used the previous utility packages should switch to the corresponding `tenzir::*` operator names.

*By @mavam and @codex in #147.*

### Contexts declared in the configuration

The package no longer ships the `process-name-baselines` context, and `tenzir::osint::update_context` no longer takes `max_age`, because Tenzir 7 declares contexts and their timeouts in the configuration. Declare both lookup tables there:

```yaml
# contexts/ocsf-osint.yaml
type: lookup-table
persist-interval: 5min
write-timeout: 30d
```

```yaml
# contexts/process-name-baselines.yaml
type: lookup-table
persist-interval: 5min
```

Before:

```tql
tenzir::osint::update_context max_age=30d
```

After:

```tql
tenzir::osint::update_context
```

Since a context can't erase entries, a removed indicator now replaces its entry with one that has already expired, and `tenzir::osint::enrich` ignores it.

*By @mavam in #233.*

## 🚀 Features

### Agent credential exposure detection

The `tenzir` package now flags credential or secret material appearing in an AI agent's prompt, completion, or tool argument as an OCSF Detection Finding.

```tql
subscribe "ocsf"
tenzir::detect::agent::credential_exposure
publish "findings"
```

The detector matches structural credential signatures only, such as an AWS access key ID, a PEM private key header, or a GitHub or Slack token prefix, never the surrounding language. The matched text never leaves the operator: the finding carries the credential kind and a SHA-256 evidence hash, so repeated leaks of the same secret correlate without exposing it downstream.

Lives in the `tenzir::detect::agent` namespace, alongside the network detectors in `tenzir::detect::network`.

*By @zedoraps in #188.*

### Agent hidden Unicode detection operator

The `tenzir` package now flags invisible Unicode formatting characters in agent prompts, responses, and file edits:

```tql
subscribe "ocsf"
tenzir::detect::agent::hidden_unicode
publish "findings"
```

A single pattern over Unicode category "Format" catches zero-width spaces, bidirectional overrides, and Unicode tag characters in one check, the three families documented for hiding instructions from human review while an LLM still parses them. The detector reads `message_context.prompt_text`, `message_context.response_text`, and `file_diff` on any event carrying the AI Operation profile, which requires the source package's `include_content` parameter to be enabled.

Lives in the new `tenzir::detect::agent` namespace, alongside `tenzir::detect::network` and `tenzir::detect::behavior`.

*By @codex.*

### Agent hook settings-override detection

The `tenzir` package now flags a Claude Code hook registered through a CLI settings override (`hook_source == "flagSettings"`) rather than a committed project or user settings file.

```tql
subscribe "ocsf"
tenzir::detect::agent::hook_settings_override
publish "findings"
```

This settings tier ranks above committed project and user files in Claude Code's precedence order, populated by the documented `--settings` CLI flag. That's a legitimate, documented automation mechanism, so expect this to fire on CI/CD and scripted invocations; it's best read as an audit signal for interactive sessions, not a universal severity claim.

*By @claude.*

### Agent permissive mode detection

The `tenzir` package now flags an agent session assigned a full-autonomy permission or sandbox mode, such as Claude Code's `bypassPermissions` or Codex's `danger-full-access` sandbox.

```tql
subscribe "ocsf"
tenzir::detect::agent::permissive_mode
publish "findings"
```

The detector is a static policy check on the currently-assigned privileges, independent of how or why the mode was assigned — it fires the same whether a person chose it deliberately or a repo's checked-in configuration set it.

Detectors live in the `tenzir::detect::agent` namespace, alongside `tenzir::detect::network` and `tenzir::detect::behavior`. Every finding carries MITRE ATT&CK tactic and technique mappings in `finding_info.attacks` and a versioned analytic identity for traceability.

*By @claude.*

### Categorical behavioral baseline operators

The `tenzir` package now provides three composable operators for categorical behavioral baselines in the `tenzir::detect::behavior::categorical` namespace. Two records form the contract between them:

- `model` summarizes a finite input into one row per entity of the shape `{entity, baseline: {distribution: <frequency_table>, trained_at: <time>}}`.
- `score` reads such a `baseline` record from the event and writes a self-describing result `{feature, entity, value, status, baseline_count, familiarity, drift, score}` into a caller-selected field. With `window_size`, it also models each entity's current window, mixes its Jensen-Shannon drift into the score, and records the window as `{start, end}` in the result.
- `finding` turns that result into an OCSF Detection Finding. Without arguments it replaces the event, like the `normalize` operators of our source packages; with `into`, it writes the finding next to the event.

Storage stays in the caller's pipeline. Whether a freshly modeled baseline replaces the stored row or accumulates into it is one line: `baseline.distribution = model_merge([previous?.distribution?, baseline.distribution])`. The examples store baselines in a `process-name-baselines` lookup table that you declare in your configuration.

For an unbounded stream, score each window before you merge its observations into the context. Keeping both steps in one pipeline prevents the current window from training its own baseline:

```tql
subscribe "ocsf"
where class_uid == 1007 and activity_id == 1
context_enrich "process-name-baselines",
  key=device.hostname,
  into=baseline
tenzir::detect::behavior::categorical::score \
  entity=device.hostname,
  feature=process.name,
  feature_name="process.name",
  baseline=baseline,
  window_size=5min,
  into=behavior
fork {
  where behavior.status == "ready" and behavior.score >= 0.5
  tenzir::detect::behavior::categorical::finding result=behavior
  deduplicate finding_info.uid, create_timeout=1h
  publish "findings"
}
window size=1min {
  tenzir::detect::behavior::categorical::model \
    entity=device.hostname,
    feature=process.name
}
context_enrich "process-name-baselines", key=entity, into=previous
baseline.distribution = model_merge([
  previous?.distribution?,
  baseline.distribution,
])
drop previous
context_update "process-name-baselines", key=entity, value=baseline
```

The `score` operator classifies an observation as missing, immature, stale, or ready. It leaves observations with a null feature value unscored. For ready observations, it measures how familiar the feature value is and, when `window_size` is set, mixes that local score with the drift of the entity's current window from the baseline. A window delays each event until the window closes. The result goes into a caller-selected field, so several behavioral detectors can score the same event without colliding; set `feature_name` per detector so each one identifies its own analytic.

The `finding` operator derives `finding_info.uid` from the feature, entity, value, and window of the result, so repeated launches of the same unfamiliar value within one window share one identity that `deduplicate finding_info.uid` collapses. A scored window is also reported as `start_time` and `end_time`. The analytic carries `type_id: 2` (Behavioral) and `uid: tenzir::detect::behavior::abnormal_features:<feature_name>`.

The baseline uses the frequency table's own `count` as its sample count and ignores observations without an entity identifier or feature value. Empty windows therefore neither make a model ready nor refresh an existing baseline. The `min_samples` argument must be positive. The `drift_weight` argument must stay between `0.0` and `1.0`, which keeps the composite score and the resulting OCSF risk score bounded.

*By @mavam in #185.*

### OCSF network detection operators

The `tenzir` package now turns OCSF Network Activity streams into Detection Findings for scan fan-out, beacon cadence, long connections, and outbound volume bursts.

Run any detector as a user-defined operator between your normalized stream and the findings topic:

```tql
subscribe "ocsf"
tenzir::detect::network::beacon_cadence
publish "findings"
```

Each operator exposes its time window, late-event tolerance, and detection thresholds as named arguments for environment-specific tuning.

The beacon and volume detectors measure originator traffic via `traffic.bytes_out`, the source-to-destination byte count that the NetFlow, Zeek, and Suricata mappings populate consistently.

Detectors live in the `tenzir::detect::network` namespace, leaving room for future detector families over other OCSF classes. Every finding carries MITRE ATT&CK tactic and technique mappings in `finding_info.attacks` and a versioned analytic identity for traceability.

*By @mavam and @codex in #172.*

## 🐞 Bug fixes

### OSINT enrichment honors IP matches and expiration

The OSINT lookup table now honors indicator expiration, and IP enrichment works with every OSINT feed.

- `tenzir::osint::enrich` matches IP addresses against the string values that OSINT mappers store, so network events now get IP indicator matches. It also ignores indicators past their `expiration_time` and adds `osint` and the `osint` profile only to events with a match.
- `tenzir::osint::update_context` no longer warns about events without a status.

*By @mavam in #196.*
